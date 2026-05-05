export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  const { url } = req.query;
  if (!url) return res.status(400).json({ error: 'No URL' });

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);
    const response = await fetch(url, {
      headers: { 'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)' },
      signal: controller.signal,
      redirect: 'follow',
    });
    clearTimeout(timeout);
    const html = await response.text();
    const match = html.match(/<title[^>]*>([^<]*)<\/title>/i);
    const title = match
      ? match[1].replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&#(\d+);/g,(_,n)=>String.fromCharCode(n)).trim()
      : null;
    res.json({ title });
  } catch (e) {
    res.json({ title: null });
  }
}
