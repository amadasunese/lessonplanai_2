from PIL import Image

# Open the original image
img_path = '/static/images/lessonplan_background.jpeg'
img = Image.open(img_path)

# Resize the image to specific dimensions
resized_img = img.resize((502, 163))

# Save the resized image
resized_img_path = "/static/images/resized_502x163.png"
resized_img.save(resized_img_path)

resized_img_path