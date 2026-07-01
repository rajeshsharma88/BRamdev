const express = require('express');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const app = express();
const PORT = 3000;
const LEADS_FILE = path.join(__dirname, 'leads.json');
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'admin123';
const TOKEN = crypto.randomBytes(16).toString('hex');

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

function loadLeads() {
  try { return JSON.parse(fs.readFileSync(LEADS_FILE, 'utf-8')); }
  catch { return []; }
}

function saveLeads(leads) {
  fs.writeFileSync(LEADS_FILE, JSON.stringify(leads, null, 2), 'utf-8');
}

function isAuth(req) {
  return req.headers.cookie?.includes(`token=${TOKEN}`);
}

function requireAuth(req, res, next) {
  if (!isAuth(req)) {
    return res.redirect('/admin');
  }
  next();
}

app.post('/api/lead', (req, res) => {
  const { age, name, phone, city } = req.body;
  if (!age || !name || !phone || !city) {
    return res.status(400).json({ error: 'All fields are required' });
  }
  const leads = loadLeads();
  const lead = {
    id: Date.now(), age, name, phone, city,
    product: 'Aarogya Champ', price: '₹399',
    timestamp: new Date().toLocaleString('hi-IN', { timeZone: 'Asia/Kolkata' })
  };
  leads.push(lead);
  saveLeads(leads);
  console.log(`New lead: ${name} (${phone}) from ${city}`);
  res.json({ success: true, id: lead.id });
});

app.post('/admin/login', (req, res) => {
  if (req.body.password === ADMIN_PASSWORD) {
    res.setHeader('Set-Cookie', `token=${TOKEN}; HttpOnly; Path=/; Max-Age=86400`);
    res.redirect('/admin/dashboard');
  } else {
    res.send('<html><body><h2>गलत पासवर्ड</h2><a href="/admin">वापस जाएं</a></body></html>');
  }
});

app.get('/admin/logout', (req, res) => {
  res.setHeader('Set-Cookie', `token=; HttpOnly; Path=/; Max-Age=0`);
  res.redirect('/admin');
});

app.get('/admin', (req, res) => {
  if (isAuth(req)) return res.redirect('/admin/dashboard');
  res.send(`<!DOCTYPE html>
<html lang="hi">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Admin Login</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:system-ui,Arial,sans-serif;background:linear-gradient(135deg,#1a1a2e,#16213e);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}.login-box{background:#fff;padding:35px;border-radius:20px;box-shadow:0 20px 60px rgba(0,0,0,0.3);width:100%;max-width:380px;text-align:center}.login-box h2{color:#1a1a2e;margin-bottom:20px;font-size:22px}.login-box input{width:100%;padding:14px 16px;border:2px solid #e0e0e0;border-radius:12px;font-size:16px;margin-bottom:16px;outline:none;transition:.2s}.login-box input:focus{border-color:#c40000;box-shadow:0 0 0 3px rgba(196,0,0,0.1)}.login-box button{width:100%;padding:14px;border:none;border-radius:12px;background:linear-gradient(135deg,#c40000,#ff2b2b);color:#fff;font-size:17px;font-weight:700;cursor:pointer;transition:.3s}.login-box button:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(196,0,0,0.3)}.login-box .hint{margin-top:14px;font-size:13px;color:#888}</style></head>
<body><div class="login-box"><h2>&#x1F512; Admin Login</h2><form method="POST" action="/admin/login"><input type="password" name="password" placeholder="Password" required><button type="submit">Login</button></form><div class="hint">Default: admin123</div></div></body></html>`);
});

app.get('/admin/dashboard', requireAuth, (req, res) => {
  const leads = loadLeads();
  const rows = leads.map(l => `<tr>
    <td>${l.id}</td>
    <td>${l.name}</td>
    <td>${l.phone}</td>
    <td>${l.city}</td>
    <td>${l.age}</td>
    <td>${l.timestamp}</td>
  </tr>`).join('');
  res.send(`<!DOCTYPE html>
<html lang="hi">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Leads Dashboard</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:system-ui,Arial,sans-serif;background:#f5f5f5;padding:20px}.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:10px}.header h1{font-size:22px;color:#1a1a2e}.header .actions{display:flex;gap:10px}.btn{display:inline-block;padding:10px 20px;border:none;border-radius:10px;font-size:14px;font-weight:600;cursor:pointer;text-decoration:none;transition:.2s}.btn-download{background:#28a745;color:#fff}.btn-download:hover{background:#218838}.btn-logout{background:#6c757d;color:#fff}.btn-logout:hover{background:#5a6268}.stats{display:flex;gap:16px;margin-bottom:20px;flex-wrap:wrap}.stat-card{background:#fff;padding:16px 22px;border-radius:14px;box-shadow:0 2px 10px rgba(0,0,0,0.05);flex:1;min-width:120px;text-align:center}.stat-card .num{font-size:28px;font-weight:800;color:#c40000}.stat-card .label{font-size:13px;color:#888;margin-top:4px}.table-wrap{background:#fff;border-radius:16px;box-shadow:0 2px 15px rgba(0,0,0,0.06);overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:14px}th{background:#f8f8f8;color:#555;font-weight:600;text-align:left;padding:14px 16px;border-bottom:2px solid #eee}td{padding:12px 16px;border-bottom:1px solid #f0f0f0;color:#333}tr:hover td{background:#fafafa}.empty{text-align:center;padding:40px;color:#888;font-size:16px}@media(max-width:600px){th,td{font-size:13px;padding:10px 12px}.header h1{font-size:18px}}</style></head>
<body>
<div class="header"><h1>&#x1F4CB; Leads Dashboard</h1><div class="actions"><a class="btn btn-download" href="/api/leads/download">&#x1F4E5; Download CSV</a><a class="btn btn-logout" href="/admin/logout">Logout</a></div></div>
<div class="stats"><div class="stat-card"><div class="num">${leads.length}</div><div class="label">Total Leads</div></div><div class="stat-card"><div class="num">${new Set(leads.map(l=>l.city)).size}</div><div class="label">Cities</div></div><div class="stat-card"><div class="num">${new Set(leads.map(l=>l.phone)).size}</div><div class="label">Unique Phones</div></div></div>
<div class="table-wrap">${leads.length ? '<table><thead><tr><th>ID</th><th>Name</th><th>Phone</th><th>City</th><th>Age</th><th>Timestamp</th></tr></thead><tbody>' + rows + '</tbody></table>' : '<div class="empty">&#x1F4ED; No leads yet</div>'}</div>
</body></html>`);
});

app.get('/api/leads', requireAuth, (req, res) => {
  res.json(loadLeads());
});

app.get('/api/leads/download', requireAuth, (req, res) => {
  const leads = loadLeads();
  const header = 'ID,Name,Phone,City,Age,Product,Price,Timestamp\n';
  const rows = leads.map(l =>
    `${l.id},"${l.name}",${l.phone},"${l.city}","${l.age}","${l.product}","${l.price}","${l.timestamp}"`
  ).join('\n');
  res.setHeader('Content-Type', 'text/csv; charset=utf-8');
  res.setHeader('Content-Disposition', 'attachment; filename=leads.csv');
  res.send('\uFEFF' + header + rows);
});

app.use(express.static(__dirname));

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
  console.log(`  Admin login:    http://localhost:${PORT}/admin`);
  console.log(`  Form submits:   POST /api/lead`);
  console.log(`Default password: admin123`);
  console.log(`Set env ADMIN_PASSWORD to change it`);
});
