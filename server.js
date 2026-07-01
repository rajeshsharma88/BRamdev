const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;
const LEADS_FILE = path.join(__dirname, 'leads.json');

app.use(express.json());
app.use(express.static(__dirname));

function loadLeads() {
  try {
    return JSON.parse(fs.readFileSync(LEADS_FILE, 'utf-8'));
  } catch {
    return [];
  }
}

function saveLeads(leads) {
  fs.writeFileSync(LEADS_FILE, JSON.stringify(leads, null, 2), 'utf-8');
}

app.post('/api/lead', (req, res) => {
  const { age, name, phone, city } = req.body;
  if (!age || !name || !phone || !city) {
    return res.status(400).json({ error: 'All fields are required' });
  }
  const leads = loadLeads();
  const lead = {
    id: Date.now(),
    age,
    name,
    phone,
    city,
    product: 'Aarogya Champ',
    price: '₹399',
    timestamp: new Date().toLocaleString('hi-IN', { timeZone: 'Asia/Kolkata' })
  };
  leads.push(lead);
  saveLeads(leads);
  console.log(`New lead: ${name} (${phone}) from ${city}`);
  res.json({ success: true, id: lead.id });
});

app.get('/api/leads', (req, res) => {
  const leads = loadLeads();
  res.json(leads);
});

app.get('/api/leads/download', (req, res) => {
  const leads = loadLeads();
  const header = 'ID,Name,Phone,City,Age,Product,Price,Timestamp\n';
  const rows = leads.map(l =>
    `${l.id},"${l.name}",${l.phone},"${l.city}","${l.age}","${l.product}","${l.price}","${l.timestamp}"`
  ).join('\n');
  const csv = '\uFEFF' + header + rows;
  res.setHeader('Content-Type', 'text/csv; charset=utf-8');
  res.setHeader('Content-Disposition', 'attachment; filename=leads.csv');
  res.send(csv);
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
  console.log(`  Form submissions: POST /api/lead`);
  console.log(`  View leads:       GET /api/leads`);
  console.log(`  Download CSV:     GET /api/leads/download`);
});
