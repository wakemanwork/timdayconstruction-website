// Contact form handler (fix log F4, DESIGN.md 6.21). Vercel Function, Node.js runtime,
// Web-standard `export default { fetch(request) }` handler (Vercel docs: Functions API reference).
// No dependencies: Turnstile and Resend are called with fetch.
//
// Flow: POST only → honeypot → field validation → Turnstile verification → email via Resend.
// Responses: JSON ({ ok } or { ok:false, error }) when the client asks for JSON (the enhanced form
// sends Accept: application/json); otherwise a 303 redirect to /contact/?sent=1 or ?error=<code>
// so the form also works as a plain HTML POST.
//
// Environment variables:
//   RESEND_API_KEY        required   Resend API key
//   CONTACT_FROM          required   verified sender, e.g. "Tim Day Construction <website@timdayconstruction.co.uk>"
//   CONTACT_TO            optional   recipient(s), comma-separated; default info@timdayconstruction.co.uk
//   TURNSTILE_SECRET_KEY  required in production (VERCEL_ENV=production); skipped elsewhere when unset
//   PUBLIC_TURNSTILE_SITE_KEY (build time, used by the form component, not here)

const LIMITS = { 'your-name': 400, 'your-email': 400, 'your-subject': 400, 'your-message': 2000 };
const REQUIRED = ['your-name', 'your-email', 'your-subject']; // as on the live CF7 form; message is optional
const EMAIL_RE = /^[^\s@<>()[\]\\,;:"]+@[^\s@<>()[\]\\,;:"]+\.[^\s@<>()[\]\\,;:"]{2,}$/;

function wantsJson(request) {
  return (request.headers.get('accept') || '').includes('application/json');
}

function reply(request, ok, error, status = 200) {
  if (wantsJson(request)) {
    return Response.json(ok ? { ok: true } : { ok: false, error }, { status, headers: { 'Cache-Control': 'no-store' } });
  }
  const url = new URL('/contact/', request.url);
  url.search = ok ? 'sent=1' : `error=${encodeURIComponent(error)}`;
  url.hash = 'contact-form';
  return new Response(null, { status: 303, headers: { Location: url.pathname + url.search + url.hash, 'Cache-Control': 'no-store' } });
}

const oneLine = (s) => s.replace(/[\r\n]+/g, ' ').trim();

async function verifyTurnstile(token, ip) {
  const secret = process.env.TURNSTILE_SECRET_KEY;
  if (!secret) return process.env.VERCEL_ENV !== 'production'; // local and preview without a key: allow
  if (!token) return false;
  const body = new URLSearchParams({ secret, response: token });
  if (ip) body.set('remoteip', ip);
  try {
    const res = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', { method: 'POST', body });
    const data = await res.json();
    return data.success === true;
  } catch {
    return false;
  }
}

export default {
  async fetch(request) {
    if (request.method !== 'POST') {
      return new Response('Method Not Allowed', { status: 405, headers: { Allow: 'POST' } });
    }

    let form;
    try {
      form = await request.formData();
    } catch {
      return reply(request, false, 'invalid', 400);
    }
    const get = (k) => (typeof form.get(k) === 'string' ? form.get(k).trim() : '');

    // Honeypot: bots fill every field. Pretend success so they learn nothing; send nothing.
    if (get('your-website')) return reply(request, true);

    const data = {
      name: oneLine(get('your-name')),
      email: oneLine(get('your-email')),
      subject: oneLine(get('your-subject')),
      message: get('your-message'),
      page: oneLine(get('page')).slice(0, 200),
    };
    for (const k of REQUIRED) if (!get(k)) return reply(request, false, 'invalid', 422);
    for (const [k, max] of Object.entries(LIMITS)) if (get(k).length > max) return reply(request, false, 'invalid', 422);
    if (!EMAIL_RE.test(data.email)) return reply(request, false, 'email', 422);

    const ip = (request.headers.get('x-forwarded-for') || '').split(',')[0].trim() || undefined;
    if (!(await verifyTurnstile(get('cf-turnstile-response'), ip))) return reply(request, false, 'verify', 403);

    const apiKey = process.env.RESEND_API_KEY;
    const from = process.env.CONTACT_FROM;
    const to = (process.env.CONTACT_TO || 'info@timdayconstruction.co.uk').split(',').map((s) => s.trim()).filter(Boolean);
    if (!apiKey || !from) {
      console.error('contact: RESEND_API_KEY or CONTACT_FROM is not set');
      return reply(request, false, 'failed', 500);
    }

    const text = [
      `Name: ${data.name}`,
      `Email: ${data.email}`,
      `Subject: ${data.subject}`,
      `Sent from: https://timdayconstruction.co.uk${data.page || '/contact/'}`,
      '',
      data.message || '(No message)',
    ].join('\n');

    try {
      const res = await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: { Authorization: `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          from,
          to,
          reply_to: data.email,
          subject: `Website enquiry: ${data.subject}`.slice(0, 250),
          text,
        }),
      });
      if (!res.ok) {
        console.error('contact: Resend error', res.status, await res.text().catch(() => ''));
        return reply(request, false, 'failed', 502);
      }
    } catch (err) {
      console.error('contact: Resend request failed', err);
      return reply(request, false, 'failed', 502);
    }
    return reply(request, true);
  },
};
