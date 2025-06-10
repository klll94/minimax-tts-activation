// Vercel Serverless Function
module.exports = (req, res) => {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  if (req.method === 'GET') {
    return res.status(200).json({ message: 'API is working' });
  }
  
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  const { activation_code } = req.body || {};
  
  if (!activation_code) {
    return res.status(400).json({ 
      success: false, 
      message: '请提供激活码' 
    });
  }
  
  // 测试激活码
  const validCodes = [
    "23456789ABCDEFG",
    "A23456789BCDEFG", 
    "35X3M278XQNFLEQ"
  ];
  
  if (validCodes.includes(activation_code)) {
    res.status(200).json({
      success: true,
      message: "激活码验证成功",
      data: {
        activation_id: "376d46c9-0000-0000-0000-000000000000",
        generated_date: "2025-06-10T14:29:32",
        expire_date: "2026-06-10T14:29:32",
        days_valid: 365,
        version: "3.0"
      }
    });
  } else {
    res.status(400).json({
      success: false,
      message: "激活码无效"
    });
  }
}; 