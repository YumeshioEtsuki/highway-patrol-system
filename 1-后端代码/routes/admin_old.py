# routes/admin.py

import base64
from flask import Blueprint, request, jsonify, send_file, Response
import io
from models.tasks import (
    mark_record_as_processing,
    mark_record_as_completed,
    get_patrol_list_admin,
    export_patrol_records_to_excel,
    stream_verify_database,
    stream_get_database_status,
    stream_reinit_database_with_step
)
from utils.utils import reinit_database, verify_database, get_database_status, get_db_connection

admin_bp = Blueprint('admin', __name__, url_prefix='/api')

# ========================
# 管理员业务接口
# ========================

@admin_bp.route('/patrol/<int:record_id>/process', methods=['POST'])
def api_mark_as_processing(record_id):
    try:
        success = mark_record_as_processing(record_id)
        if not success:
            return jsonify({'error': '记录不存在或状态不可变'}), 400
        return jsonify({'success': True})
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        return jsonify({'error': '操作失败'}), 500

@admin_bp.route('/patrol/<int:record_id>/complete', methods=['POST'])
def api_mark_as_completed(record_id):
    data = request.get_json()
    remark = data.get('remark', '').strip()
    if not remark:
        return jsonify({'error': '请填写处理备注'}), 400
    try:
        success = mark_record_as_completed(record_id, process_note=remark)
        if not success:
            return jsonify({'error': '记录未处于“处理中”状态'}), 400
        return jsonify({'success': True})
    except Exception as e:
        print(f"❌ 完成失败: {e}")
        return jsonify({'error': '操作失败'}), 500

@admin_bp.route('/patrol/list', methods=['GET'])
def api_patrol_list_admin():
    status_filter = request.args.get('status')
    try:
        records = get_patrol_list_admin(status_filter=status_filter)
        return jsonify(records)
    except Exception as e:
        print(f"❌ Admin list error: {e}")
        return jsonify({'error': '查询失败'}), 500

@admin_bp.route('/export/excel')
def export_excel():
    try:
        filters = {}
        if request.args.get('start_date'):
            filters['start_date'] = request.args['start_date']
        if request.args.get('end_date'):
            filters['end_date'] = request.args['end_date']
        if request.args.get('segment_id'):
            filters['segment_id'] = int(request.args['segment_id'])
        if request.args.get('status'):
            filters['status'] = request.args['status']

        excel_data = export_patrol_records_to_excel(filters)
        return send_file(
            io.BytesIO(excel_data),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='公路巡查记录.xlsx'
        )
    except Exception as e:
        print(f"❌ 导出失败: {e}")
        return jsonify({'error': '导出失败'}), 500

# ========================
# 数据库管理接口（原在 app.py）
# ========================

@admin_bp.route('/reinit')
def reinit():
    step = request.args.get('step', default='all')
    if step == '1':
        step = 1
    elif step == 'all':
        step = 'all'
    result = reinit_database(step=step, skip_read_only_queries=True)
    return jsonify(result)

@admin_bp.route('/verify')
def verify():
    result = verify_database()
    return jsonify(result)

@admin_bp.route('/status')
def status():
    try:
        result = get_database_status()
        return jsonify(result)
    except Exception as e:
        print(f"❌ /api/status 出错: {e}")
        return jsonify({
            'status': 'error',
            'message': '服务器内部错误',
            'details': str(e),
            'execution_time': 0
        })

# ========================
# SSE 流式接口
# ========================

@admin_bp.route('/reinit/stream')
def reinit_stream():
    step = request.args.get('step', default='all')
    return stream_reinit_database_with_step(step)

@admin_bp.route('/verify/stream')
def verify_stream():
    return stream_verify_database()

@admin_bp.route('/status/stream')
def status_stream():
    return stream_get_database_status()