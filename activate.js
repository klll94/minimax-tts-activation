// 激活码激活API - 使用后失效
const { createClient } = require('@supabase/supabase-js')

const supabaseUrl = process.env.SUPABASE_URL
const supabaseKey = process.env.SUPABASE_ANON_KEY

module.exports = async (req, res) => {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const supabase = createClient(supabaseUrl, supabaseKey)
  const { activation_code, machine_id, user_info } = req.body || {};
  
  if (!activation_code) {
    return res.status(400).json({ 
      success: false, 
      message: '请提供激活码' 
    });
  }

  if (!machine_id) {
    return res.status(400).json({ 
      success: false, 
      message: '请提供机器标识' 
    });
  }

  try {
    // 1. 检查激活码是否存在且有效
    const { data: codeData, error: codeError } = await supabase
      .from('activation_codes')
      .select('*')
      .eq('code', activation_code)
      .single();

    if (codeError || !codeData) {
      return res.status(400).json({
        success: false,
        message: '激活码不存在'
      });
    }

    // 2. 检查激活码状态
    if (codeData.status === 'used') {
      return res.status(400).json({
        success: false,
        message: '激活码已被使用'
      });
    }

    if (codeData.status === 'expired') {
      return res.status(400).json({
        success: false,
        message: '激活码已过期'
      });
    }

    // 3. 检查是否过期
    if (new Date(codeData.expire_date) < new Date()) {
      // 更新状态为过期
      await supabase
        .from('activation_codes')
        .update({ status: 'expired' })
        .eq('id', codeData.id);
        
      return res.status(400).json({
        success: false,
        message: '激活码已过期'
      });
    }

    // 4. 检查是否已经达到最大激活次数
    if (codeData.current_activations >= codeData.max_activations) {
      await supabase
        .from('activation_codes')
        .update({ status: 'used' })
        .eq('id', codeData.id);
        
      return res.status(400).json({
        success: false,
        message: '激活码使用次数已达上限'
      });
    }

    // 5. 检查是否已经在此机器上激活过
    const { data: existingRecord } = await supabase
      .from('activation_records')
      .select('*')
      .eq('code', activation_code)
      .eq('machine_id', machine_id)
      .eq('status', 'active');

    if (existingRecord && existingRecord.length > 0) {
      return res.status(400).json({
        success: false,
        message: '该激活码已在此设备上使用过'
      });
    }

    // 6. 执行激活 - 创建激活记录
    const { data: recordData, error: recordError } = await supabase
      .from('activation_records')
      .insert({
        activation_code_id: codeData.id,
        code: activation_code,
        machine_id: machine_id,
        ip_address: req.headers['x-forwarded-for'] || req.connection.remoteAddress,
        user_agent: req.headers['user-agent'],
        activation_data: user_info || {}
      })
      .select()
      .single();

    if (recordError) {
      return res.status(500).json({
        success: false,
        message: '激活记录创建失败'
      });
    }

    // 7. 更新激活码状态
    const newActivationCount = codeData.current_activations + 1;
    const newStatus = newActivationCount >= codeData.max_activations ? 'used' : 'unused';
    
    await supabase
      .from('activation_codes')
      .update({ 
        current_activations: newActivationCount,
        status: newStatus
      })
      .eq('id', codeData.id);

    // 8. 返回成功结果
    return res.status(200).json({
      success: true,
      message: '激活成功',
      data: {
        activation_id: recordData.id,
        activated_at: recordData.activated_at,
        expire_date: codeData.expire_date,
        version: codeData.version,
        machine_id: machine_id,
        remaining_activations: codeData.max_activations - newActivationCount
      }
    });

  } catch (error) {
    console.error('Activation error:', error);
    return res.status(500).json({
      success: false,
      message: '服务器内部错误'
    });
  }
} 