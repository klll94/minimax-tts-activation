// Next.js API route for status query
export default function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }
  
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }
  
  const { activation_code } = req.body;
  
  if (!activation_code) {
    res.status(400).json({ 
      success: false, 
      message: '请提供激活码' 
    });
    return;
  }
  
  // Test activation codes
  const validCodes = [
    "23456789ABCDEFG",
    "A23456789BCDEFG", 
    "35X3M278XQNFLEQ"
  ];
  
  if (validCodes.includes(activation_code)) {
    res.status(200).json({
      success: true,
      message: "激活码状态查询成功",
      data: {
        status: "active",
        activation_id: "376d46c9-0000-0000-0000-000000000000",
        generated_date: "2025-06-10T14:29:32",
        expire_date: "2026-06-10T14:29:32",
        days_remaining: 365,
        version: "3.0"
      }
    });
  } else {
    res.status(400).json({
      success: false,
      message: "激活码不存在或已过期"
    });
  }
} 