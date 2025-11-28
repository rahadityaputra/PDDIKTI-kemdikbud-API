from flask import Flask, jsonify, request
from flask_cors import CORS
from pddiktipy import api
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def create_error_response(message: str, status_code: int = 400) -> tuple:
    """Create standardized error response"""
    return jsonify({
        'success': False,
        'error': message,
        'data': None
    }), status_code

def create_success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """Create standardized success response"""
    return jsonify({
        'success': True,
        'message': message,
        'data': data
    })

@app.route('/')
def home():
    """API Information endpoint"""
    return jsonify({
        'name': 'PDDIKTI REST API',
        'version': '1.0.0',
        'description': 'REST API wrapper for PDDIKTI (Pangkalan Data Pendidikan Tinggi) Indonesia',
        'endpoints': {
            'universities': {
                'search': '/api/v1/universities/search?q=<keyword>',
                'detail': '/api/v1/universities/<university_id>',
                'programs': '/api/v1/universities/<university_id>/programs?semester=<semester>',
                'logo': '/api/v1/universities/<university_id>/logo',
                'statistics': '/api/v1/universities/<university_id>/stats'
            },
            'students': {
                'search': '/api/v1/students/search?q=<keyword>',
                'detail': '/api/v1/students/<student_id>'
            },
            'lecturers': {
                'search': '/api/v1/lecturers/search?q=<keyword>',
                'profile': '/api/v1/lecturers/<lecturer_id>',
                'research': '/api/v1/lecturers/<lecturer_id>/research'
            },
            'programs': {
                'search': '/api/v1/programs/search?q=<keyword>',
                'detail': '/api/v1/programs/<program_id>'
            },
            'search': {
                'all': '/api/v1/search?q=<keyword>'
            },
            'statistics': {
                'counts': '/api/v1/statistics/counts',
                'visualizations': '/api/v1/statistics/visualizations'
            }
        }
    })

# ========== UNIVERSITIES ENDPOINTS ==========

@app.route('/api/v1/universities/search')
def search_universities():
    """Search universities by keyword"""
    keyword = request.args.get('q', '').strip()

    print(keyword)
    
    if not keyword:
        return create_error_response("Query parameter 'q' is required")
    try:
        with api() as client:
            result = client.search_pt(keyword)
            
            if result:
                # Handle both dictionary and list responses
                if isinstance(result, dict) and result.get('data'):
                    return create_success_response(
                        result, 
                        f"Found {len(result['data'])} universities matching '{keyword}'"
                    )
                elif isinstance(result, list) and len(result) > 0:
                    # If result is a list, wrap it in the expected format
                    formatted_result = {'data': result}
                    return create_success_response(
                        formatted_result, 
                        f"Found {len(result)} universities matching '{keyword}'"
                    )
                else:
                    return create_success_response(
                        {'data': []}, 
                        f"No universities found matching '{keyword}'"
                    )
            else:
                return create_success_response(
                    {'data': []}, 
                    f"No universities found matching '{keyword}'"
                )
                
    except Exception as e:
        logger.error(f"Error searching universities: {e}")
        return create_error_response(f"Internal server error: {str(e)}", 500)

@app.route('/api/v1/universities/<university_id>')
def get_university_detail(university_id):
    """Get detailed information about a university"""
    try:
        with api() as client:
            result = client.get_detail_pt(university_id)
            
            if result:
                return create_success_response(result, "University details retrieved successfully")
            else:
                return create_error_response("University not found", 404)
                
    except Exception as e:
        logger.error(f"Error getting university detail: {e}")
        return create_error_response(f"Internal server error: {str(e)}", 500)

@app.route('/api/v1/universities/<university_id>/programs')
def get_university_programs(university_id):
    """Get study programs offered by a university"""
    semester = request.args.get('semester', '')
    
    if not semester:
        return create_error_response("Query parameter 'semester' is required (format: YYYYS, e.g., 20241)")
    
    try:
        with api() as client:
            result = client.get_prodi_pt(university_id, semester)
            if result and result.get('data'):
                return create_success_response(
                    result, 
                    f"Found {len(result['data'])} programs for semester {semester}"
                )
            else:
                return create_success_response(
                    [], 
                    f"No programs found for semester {semester}"
                )
                
    except Exception as e:
        logger.error(f"Error getting university programs: {e}")
        return create_error_response(f"Internal server error: {str(e)}", 500)

@app.route('/api/v1/universities/<university_id>/logo')
def get_university_logo(university_id):
    """Get university logo in base64 format"""
    try:
        with api() as client:
            result = client.get_logo_pt(university_id)
            
            if result:
                return create_success_response({
                    'logo_base64': result,
                    'format': 'base64'
                }, "University logo retrieved successfully")
            else:
                return create_error_response("University logo not found", 404)
                
    except Exception as e:
        logger.error(f"Error getting university logo: {e}")
        return create_error_response(f"Internal server error: {str(e)}", 500)

@app.route('/api/v1/universities/<university_id>/stats')
def get_university_stats(university_id):
    """Get comprehensive statistics about a university"""
    try:
        with api() as client:
            # Gather multiple statistics
            stats = {}
            
            # Basic counts
            student_count = client.get_jumlah_mahasiswa_pt(university_id)
            lecturer_count = client.get_jumlah_dosen_pt(university_id)
            program_count = client.get_jumlah_prodi_pt(university_id)
            
            # Ratios and rates
            ratio = client.get_rasio_pt(university_id)
            graduation_rate = client.get_graduation_rate_pt(university_id)
            cost_range = client.get_cost_range_pt(university_id)
            
            # Compile stats
            stats = {
                'students': student_count.get('jumlah_mahasiswa') if student_count else None,
                'lecturers': lecturer_count.get('jumlah_dosen') if lecturer_count else None,
                'programs': program_count.get('jumlah_prodi') if program_count else None,
                'ratio': ratio.get('rasio') if ratio else None,
                'graduation_rate': graduation_rate.get('graduation_rate') if graduation_rate else None,
                'cost_range': cost_range.get('range_biaya_kuliah') if cost_range else None
            }
            
            return create_success_response(stats, "University statistics retrieved successfully")
                
    except Exception as e:
        logger.error(f"Error getting university stats: {e}")
        return create_error_response(f"Internal server error: {str(e)}", 500)

# ========== STUDENTS ENDPOINTS ==========

@app.route('/api/v1/students/search')
def search_students():
    """Search students by keyword"""
    keyword = request.args.get('q', '').strip()
    
    if not keyword:
        return create_error_response("Query parameter 'q' is required")
    
    try:
        with api() as client:
            result = client.search_mahasiswa(keyword)
            
            if result:
                # Handle both dictionary and list responses
                if isinstance(result, dict) and result.get('data'):
                    return create_success_response(
                        result, 
                        f"Found {len(result['data'])} students matching '{keyword}'"
                    )
                elif isinstance(result, list) and len(result) > 0:
                    # If result is a list, wrap it in the expected format
                    formatted_result = {'data': result}
                    return create_success_response(
                        formatted_result, 
                        f"Found {len(result)} students matching '{keyword}'"
                    )
                else:
                    return create_success_response(
                        {'data': []}, 
                        f"No students found matching '{keyword}'"
                    )
            else:
                return create_success_response(
                    {'data': []}, 
                    f"No students found matching '{keyword}'"
                )
                
    except Exception as e:
        logger.error(f"Error searching students: {e}")
        return create_error_response(f"Internal server error: {str(e)}", 500)

@app.route('/api/v1/students/<student_id>')
def get_student_detail(student_id):
    """Get detailed information about a student"""
    try:
        with api() as client:
            result = client.get_detail_mhs(student_id)
            
            if result:
                return create_success_response(result, "Student details retrieved successfully")
            else:
                return create_error_response("Student not found", 404)
                
    except Exception as e:
        logger.error(f"Error getting student detail: {e}")
        return create_error_response(f"Internal server error: {str(e)}", 500)

# ========== LECTURERS ENDPOINTS ==========

@app.route('/api/v1/lecturers/search')
def search_lecturers():
    """Search lecturers by keyword"""
    keyword = request.args.get('q', '').strip()
    
    if not keyword:
        return create_error_response("Query parameter 'q' is required")
    
    try:
        with api() as client:
            result = client.search_dosen(keyword)
            
            if result:
                # Handle both dictionary and list responses
                if isinstance(result, dict) and result.get('data'):
                    return create_success_response(
                        result, 
                        f"Found {len(result['data'])} lecturers matching '{keyword}'"
                    )
                elif isinstance(result, list) and len(result) > 0:
                    # If result is a list, wrap it in the expected format
                    formatted_result = {'data': result}
                    return create_success_response(
                        formatted_result, 
                        f"Found {len(result)} lecturers matching '{keyword}'"
                    )
                else:
                    return create_success_response(
                        {'data': []}, 
                        f"No lecturers found matching '{keyword}'"
                    )
            else:
                return create_success_response(
                    {'data': []}, 
                    f"No lecturers found matching '{keyword}'"
                )
                
    except Exception as e:
        logger.error(f"Error searching lecturers: {e}")
        return create_error_response(f"Internal server error: {str(e)}", 500)

@app.route('/api/v1/lecturers/<lecturer_id>')
def get_lecturer_profile(lecturer_id):
    """Get detailed profile of a lecturer"""
    try:
        with api() as client:
            result = client.get_dosen_profile(lecturer_id)
            
            if result:
                return create_success_response(result, "Lecturer profile retrieved successfully")
            else:
                return create_error_response("Lecturer not found", 404)
                
    except Exception as e:
        logger.error(f"Error getting lecturer profile: {e}")
        return create_error_response(f"Internal server error: {str(e)}", 500)

@app.route('/api/v1/lecturers/<lecturer_id>/research')
def get_lecturer_research(lecturer_id):
    """Get research activities of a lecturer"""
    try:
        with api() as client:
            research = client.get_dosen_penelitian(lecturer_id)
            community_service = client.get_dosen_pengabdian(lecturer_id)
            publications = client.get_dosen_karya(lecturer_id)
            patents = client.get_dosen_paten(lecturer_id)
            
            result = {
                'research': research.get('data', []) if research else [],
                'community_service': community_service.get('data', []) if community_service else [],
                'publications': publications.get('data', []) if publications else [],
                'patents': patents.get('data', []) if patents else []
            }
            
            return create_success_response(result, "Lecturer research activities retrieved successfully")
                
    except Exception as e:
        logger.error(f"Error getting lecturer research: {e}")
        return create_error_response(f"Internal server error: {str(e)}", 500)

# ========== PROGRAMS ENDPOINTS ==========

@app.route('/api/v1/programs/search')
def search_programs():
    """Search study programs by keyword"""
    keyword = request.args.get('q', '').strip()
    
    if not keyword:
        return create_error_response("Query parameter 'q' is required")
    
    try:
        with api() as client:
            result = client.search_prodi(keyword)
            
            if result:
                # Handle both dictionary and list responses
                if isinstance(result, dict) and result.get('data'):
                    return create_success_response(
                        result, 
                        f"Found {len(result['data'])} programs matching '{keyword}'"
                    )
                elif isinstance(result, list) and len(result) > 0:
                    # If result is a list, wrap it in the expected format
                    formatted_result = {'data': result}
                    return create_success_response(
                        formatted_result, 
                        f"Found {len(result)} programs matching '{keyword}'"
                    )
                else:
                    return create_success_response(
                        {'data': []}, 
                        f"No programs found matching '{keyword}'"
                    )
            else:
                return create_success_response(
                    {'data': []}, 
                    f"No programs found matching '{keyword}'"
                )
                
    except Exception as e:
        logger.error(f"Error searching programs: {e}")
        return create_error_response(f"Internal server error: {str(e)}", 500)

@app.route('/api/v1/programs/<program_id>')
def get_program_detail(program_id):
    """Get detailed information about a study program"""
    try:
        with api() as client:
            detail = client.get_detail_prodi(program_id)
            description = client.get_desc_prodi(program_id)
            
            result = {
                'detail': detail if detail else {},
                'description': description if description else {}
            }
            
            if detail or description:
                return create_success_response(result, "Program details retrieved successfully")
            else:
                return create_error_response("Program not found", 404)
                
    except Exception as e:
        logger.error(f"Error getting program detail: {e}")
        return create_error_response(f"Internal server error: {str(e)}", 500)

# ========== GENERAL SEARCH ==========

@app.route('/api/v1/search')
def search_all():
    """Search across all categories (universities, students, lecturers, programs)"""
    keyword = request.args.get('q', '').strip()
    
    if not keyword:
        return create_error_response("Query parameter 'q' is required")
    
    try:
        with api() as client:
            result = client.search_all(keyword)
            
            if result:
                return create_success_response(result, f"Search completed for '{keyword}'")
            else:
                return create_success_response([], f"No results found for '{keyword}'")
                
    except Exception as e:
        logger.error(f"Error in global search: {e}")
        return create_error_response(f"Internal server error: {str(e)}", 500)

# ========== STATISTICS ENDPOINTS ==========

@app.route('/api/v1/statistics/counts')
def get_national_counts():
    """Get national statistics counts"""
    try:
        with api() as client:
            active_lecturers = client.get_dosen_count_active()
            active_students = client.get_mahasiswa_count_active()
            programs = client.get_prodi_count()
            universities = client.get_pt_count()
            
            result = {
                'active_lecturers': active_lecturers.get('jumlah_dosen') if active_lecturers else None,
                'active_students': active_students.get('jumlah_mahasiswa') if active_students else None,
                'programs': programs.get('jumlah') if programs else None,
                'universities': universities.get('jumlah') if universities else None
            }
            
            return create_success_response(result, "National statistics retrieved successfully")
                
    except Exception as e:
        logger.error(f"Error getting national counts: {e}")
        return create_error_response(f"Internal server error: {str(e)}", 500)

@app.route('/api/v1/statistics/visualizations')
def get_visualization_data():
    """Get data for visualizations"""
    category = request.args.get('category', 'universities')
    
    try:
        with api() as client:
            if category == 'universities':
                result = {
                    'by_form': client.get_data_pt_bentuk(),
                    'by_accreditation': client.get_data_pt_akreditasi(),
                    'by_province': client.get_data_pt_provinsi(),
                    'by_supervisor_group': client.get_data_pt_kelompok_pembina()
                }
            elif category == 'students':
                result = {
                    'by_field': client.get_data_mahasiswa_bidang(),
                    'by_gender': client.get_data_mahasiswa_jenis_kelamin(),
                    'by_level': client.get_data_mahasiswa_jenjang(),
                    'by_status': client.get_data_mahasiswa_status()
                }
            elif category == 'lecturers':
                result = {
                    'by_activity': client.get_data_dosen_keaktifan(),
                    'by_field': client.get_data_dosen_bidang(),
                    'by_gender': client.get_data_dosen_jenis_kelamin(),
                    'by_level': client.get_data_dosen_jenjang()
                }
            elif category == 'programs':
                result = {
                    'by_level': client.get_data_prodi_jenjang(),
                    'by_accreditation': client.get_data_prodi_akreditasi(),
                    'by_field': client.get_data_prodi_bidang_ilmu(),
                    'by_supervisor_group': client.get_data_prodi_kelompok_pembina()
                }
            else:
                return create_error_response("Invalid category. Valid options: universities, students, lecturers, programs")
            
            return create_success_response(result, f"Visualization data for {category} retrieved successfully")
                
    except Exception as e:
        logger.error(f"Error getting visualization data: {e}")
        return create_error_response(f"Internal server error: {str(e)}", 500)

# ========== ERROR HANDLERS ==========

@app.errorhandler(404)
def not_found(error):
    return create_error_response("Endpoint not found", 404)

@app.errorhandler(500)
def internal_error(error):
    return create_error_response("Internal server error", 500)

@app.errorhandler(400)
def bad_request(error):
    return create_error_response("Bad request", 400)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)