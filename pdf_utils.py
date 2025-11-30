import fitz
import io

MAX_FILE_SIZE_MB = 200

def check_file_size(file_obj):
  """Checks if file is within safety limits."""
  size_mb = file_obj.size / (1024 * 1024)
  if size_mb > MAX_FILE_SIZE_MB:
    return False, size_mb
  return True, size_mb

def compress_single_pdf(file_bytes, filename, quality=65, dpi=120):
  """
  Compresses a single PDF file byte stream using rasterization.
  Returns: (processed_bytes, original_mb, final_mb, reduction_percent, status_message)
  """
  try:
    # Open PDF from memory stream
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    doc_new = fitz.open()

    for page in doc:
      # Rasterize page (force white background with alpha=False)
      zoom = dpi / 72
      matrix = fitz.Matrix(zoom, zoom)
      pix = page.get_pixmap(matrix=matrix, alpha=False)

      # Convert to compressed JPEG bytes
      img_bytes = pix.tobytes("jpg", jpg_quality=quality)

      # Create new PDF page
      new_page = doc_new.new_page(width=pix.width, height=pix.height)
      new_page.insert_image(new_page.rect, stream=img_bytes)

    # Save to memory buffer
    output_buffer = io.BytesIO()
    doc_new.save(output_buffer, garbage=4, deflate=True)
    doc_new.close()
    doc.close()

    # Calculate sizes
    original_size = len(file_bytes)
    final_size = output_buffer.tell()
    
    # Logic: Keep Original if new is larger
    if final_size >= original_size:
      return file_bytes, original_size / (1024**2), original_size / (1024**2), 0.0, "MANTIDO ORIGINAL (Era menor)"
    
    # Rewind buffer to start
    output_buffer.seek(0)
    
    original_mb = original_size / (1024**2)
    final_mb = final_size / (1024**2)
    reduction = (1 - (final_size / original_size)) * 100

    return output_buffer, original_mb, final_mb, reduction, "Sucesso"

  except Exception as e:
    print(f"Error compressing {filename}: {e}")
    # Return original file in case of error, to not break the pipeline
    return file_bytes, 0, 0, 0, f"Erro: {str(e)}"

def merge_pdfs_separated(cover_object, body_objects_list):
  """
  Merges PDFs with strict order: Cover First + Sorted Body Files.
  Args:
    cover_object: Dict {'filename': str, 'bytes': bytes} OR None
    body_objects_list: List of Dicts
  """
  doc_final = fitz.open()

  # 1. Process Cover (if exists)
  if cover_object:
    try:
      stream_data = cover_object['bytes']
      if hasattr(stream_data, 'seek'): stream_data.seek(0)
      doc_temp = fitz.open(stream=stream_data, filetype="pdf")
      doc_final.insert_pdf(doc_temp)
      doc_temp.close()
    except Exception as e:
      print(f"Error merging cover: {e}")

  # 2. Process Body Files (Already sorted by frontend)
  for p_file in body_objects_list:
    try:
      stream_data = p_file['bytes']
      if hasattr(stream_data, 'seek'): stream_data.seek(0)
      doc_temp = fitz.open(stream=stream_data, filetype="pdf")
      doc_final.insert_pdf(doc_temp)
      doc_temp.close()
    except Exception as e:
      print(f"Error merging body file {p_file['filename']}: {e}")

  output_buffer = io.BytesIO()
  doc_final.save(output_buffer, garbage=4, deflate=True)
  doc_final.close()
  output_buffer.seek(0)
  
  return output_buffer