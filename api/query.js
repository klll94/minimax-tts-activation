// 查询激活记录API
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.SUPABASE_URL
const supabaseKey = process.env.SUPABASE_ANON_KEY

export default async function handler(req, res) {
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
  const { activation_code, machine_id } = req.body || {};
  
  if (!activation_code) {
    return res.status(400).json({ 
      success: false, 
      message: '请提供激活码' 
    });
  }

  try {
    // 查询激活码信息
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

    // 查询激活记录
    let query = supabase
      .from('activation_records')
      .select('*')
      .eq('code', activation_code)
      .order('activated_at', { ascending: false });

    // 如果提供了机器ID，只查询该机器的记录
    if (machine_id) {
      query = query.eq('machine_id', machine_id);
    }

    const { data: records, error: recordsError } = await query;

    if (recordsError) {
      return res.status(500).json({
        success: false,
        message: '查询记录失败'
      });
    }

    // 返回结果
    return res.status(200).json({
      success: true,
      message: '查询成功',
      data: {
        activation_code: {
          code: codeData.code,
          status: codeData.status,
          created_at: codeData.created_at,
          expire_date: codeData.expire_date,
          max_activations: codeData.max_activations,
          current_activations: codeData.current_activations,
          version: codeData.version,
          notes: codeData.notes
        },
        activation_records: records.map(record => ({
          id: record.id,
          activated_at: record.activated_at,
          machine_id: record.machine_id,
          ip_address: record.ip_address,
          status: record.status,
          activation_data: record.activation_data
        })),
        summary: {
          total_activations: records.length,
          active_activations: records.filter(r => r.status === 'active').length,
          can_activate: codeData.status === 'unused' && 
                       codeData.current_activations < codeData.max_activations &&
                       new Date(codeData.expire_date) > new Date()
        }
      }
    });

  } catch (error) {
    console.error('Query error:', error);
    return res.status(500).json({
      success: false,
      message: '服务器内部错误'
    });
  }
} 
