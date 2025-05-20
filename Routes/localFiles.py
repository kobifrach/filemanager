# # from flask import Blueprint, request, jsonify
# # # from ..database import get_db_connection

# # local_bp = Blueprint('local', __name__)  # יצירת Blueprint


# from flask import Blueprint, request, jsonify
# from ..database import get_db_connection
# from werkzeug.exceptions import NotFound
# from ..file import Node
# from flask import Blueprint, request, render_template, render_template_string, redirect, url_for, send_file, make_response, Response
# import os
# import json
# import base64
# import mimetypes
# from werkzeug.utils import secure_filename, safe_join
# from werkzeug.exceptions import NotFound
# from io import BytesIO
# from ..exceptions import OutsideDirectoryBase, InvalidFilenameError
# from ..appconfig import Flask
# from ..manager import PluginManager
# from ..database import get_db_connection
# from docx import Document
# from flask import stream_with_context
# import logging

# # הגדרת הלוגר
# logger = logging.getLogger('my_blueprint_logger')
# logger.setLevel(logging.DEBUG)
# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# ch.setFormatter(formatter)
# logger.addHandler(ch)


# local_bp = Blueprint('local', __name__)




# @local_bp.route('/users')
# def users():
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     cursor.execute('SELECT * FROM Users')
#     rows = cursor.fetchall()

#     users_list = []
#     for row in rows:
#         users_list.append({'id': row[0], 'name': row[1], 'email': row[2]})

#     conn.close()

#     return render_template('users.html', users=users_list)

# @local_bp.route('/sort/<string:property>', defaults={"path": ""})
# @local_bp.route('/sort/<string:property>/<path:path>')
# def sort(property, path):
#     try:
#         directory = Node.from_urlpath(path)
#     except OutsideDirectoryBase:
#         return NotFound()

#     if not directory.is_directory or directory.is_excluded:
#         return NotFound()

#     data = [
#         (cpath, cprop)
#         for cpath, cprop in iter_cookie_browse_sorting(request.cookies)
#         if cpath != path
#     ]
#     data.append((path, property))
#     raw_data = base64.b64encode(json.dumps(data).encode('utf-8')).decode('utf-8')

#     while len(raw_data) > 3975:
#         data.pop(0)
#         raw_data = base64.b64encode(json.dumps(data).encode('utf-8')).decode('utf-8')

#     response = redirect(url_for(".browse", path=directory.urlpath))
#     response.set_cookie('browse-sorting', raw_data)
#     return response


# @local_bp.route("/browse", defaults={"path": ""})
# @local_bp.route('/browse/<path:path>')
# def browse(path):
#     sort_property = get_cookie_browse_sorting(path, 'text')
#     sort_fnc, sort_reverse = browse_sortkey_reverse(sort_property)
#     try:
#         directory = Node.from_urlpath(path)
#         if directory.is_directory and not directory.is_excluded:
#             return stream_template(
#                 'browse.html',
#                 file=directory,
#                 sort_property=sort_property,
#                 sort_fnc=sort_fnc,
#                 sort_reverse=sort_reverse
#             )
#     except OutsideDirectoryBase:
#         pass
#     return NotFound()


# @local_bp.route("/preview/file/<path:path>")
# def preview_file(path):
#     try:
#         file = Node.from_urlpath(path)
#         if not file.is_file or file.is_excluded:
#             return NotFound()

#         file_path = getattr(file, "path", None) or getattr(file, "fullpath", None)

#         if not file_path:
#             return NotFound()

#         if file_path.endswith(".docx"):
#             doc = Document(file_path)
#             html_content = "<html><body>"
#             for para in doc.paragraphs:
#                 html_content += f"<p>{para.text}</p>"
#             html_content += "</body></html>"
#             return render_template_string(html_content)

#         mimetype, _ = mimetypes.guess_type(file_path)
#         return send_file(file_path, mimetype=mimetype, as_attachment=False)
#     except Exception as e:
#         print(f"Error: {e}")
#         return NotFound()


# @local_bp.route('/open/<path:path>', endpoint="open")
# def open_file(path):
#     try:
#         file = Node.from_urlpath(path)
#         if file.is_file and not file.is_excluded:
#             return send_from_directory(file.parent.path, file.name)
#     except OutsideDirectoryBase:
#         pass
#     return NotFound()


# @local_bp.route("/download/file/<path:path>")
# def download_file(path):
#     try:
#         file = Node.from_urlpath(path)
#         if file.is_file and not file.is_excluded:
#             return file.download()
#     except OutsideDirectoryBase:
#         pass
#     return NotFound()


# @local_bp.route("/download/directory/<path:path>.tgz")
# def download_directory(path):
#     try:
#         directory = Node.from_urlpath(path)
#         if directory.is_directory and not directory.is_excluded:
#             return directory.download()
#     except OutsideDirectoryBase:
#         pass
#     return NotFound()


# @local_bp.route("/create_folder", methods=["POST"])
# def create_folder():
#     UPLOAD_FOLDER = r"C:\Users\User\Desktop\files"
#     try:
#         folder_name = request.form.get('folder_name')
#         current_path = request.form.get('current_path')

#         if not folder_name:
#             return "Folder name is required", 400

#         if not current_path:
#             current_path = "uploads"

#         folder_path = os.path.join(UPLOAD_FOLDER, current_path, folder_name)
#         os.makedirs(folder_path, exist_ok=True)

#         doc = Document()
#         doc.add_heading(folder_name, level=1)
#         doc.save(os.path.join(folder_path, f"{folder_name}.docx"))

#         return redirect(url_for(".browse", path=current_path))

#     except Exception as e:
#         app.logger.error(f"Error during folder creation: {str(e)}")
#         return "An error occurred", 500


# @local_bp.route("/remove/<path:path>", methods=("GET", "POST"))
# def remove(path):
#     try:
#         file = Node.from_urlpath(path)
#         file.can_remove = True
#     except OutsideDirectoryBase:
#         return NotFound()

#     if not file.can_remove or file.is_excluded or not file.parent:
#         return NotFound()

#     if request.method == 'GET':
#         return render_template('remove.html', file=file)

#     file.remove()
#     return redirect(url_for(".browse", path=file.parent.urlpath))


# @local_bp.route("/upload", defaults={'path': ''}, methods=("POST",))
# @local_bp.route("/upload/<path:path>", methods=("POST",))
# def upload(path):
#     UPLOAD_FOLDER = r"C:\Users\User\Desktop\files"
#     try:
#         if not path:
#             path = "uploads"

#         folder_path = os.path.join(UPLOAD_FOLDER, path)

#         if not os.path.exists(folder_path):
#             app.logger.info(f"Creating folder: {folder_path}")
#             os.makedirs(folder_path)

#         directory = Node.from_urlpath(path)
#         directory.can_upload = True

#         if not directory.is_directory or not directory.can_upload or directory.is_excluded:
#             return NotFound()

#         for f in request.files.getlist('file[]'):
#             filename = secure_filename(f.filename)

#             if filename:
#                 filename = directory.choose_filename(filename)
#                 filepath = os.path.join(folder_path, filename)
#                 f.save(filepath)
#             else:
#                 raise InvalidFilenameError(
#                     path=directory.path,
#                     filename=f.filename
#                 )

#         return redirect(url_for(".browse", path=directory.urlpath))

#     except Exception as e:
#         app.logger.error(f"Error during file upload: {str(e)}")
#         return "An error occurred", 500

