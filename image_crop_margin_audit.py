import requests, sys, io, os, threading
from PIL import Image

def get_bottom_pixels(url):
	# Download the image from the provided URL
	try:
		response = requests.get(url)
	except:
		return None
	image = Image.open(io.BytesIO(response.content))

	# Get the image height
	image_height = image.height

	# Initialize variables to store bottom opaque and translucent pixels
	bottom_opaque_pixel = None
	bottom_translucent_pixel = None

	# Iterate through each pixel from bottom to top
	for y in range(image_height - 1, -1, -1):
		for x in range(image.width):
			pixel = image.getpixel((x, y))

			# Check if the pixel is opaque or translucent
			if len(pixel) == 4 and pixel[3] == 255:  # Opaque pixel
				if bottom_opaque_pixel is None:
					bottom_opaque_pixel = y
			elif len(pixel) == 4 and 0 < pixel[3] < 255:  # Translucent pixel
				if bottom_translucent_pixel is None:
					bottom_translucent_pixel = y

			# If both bottom opaque and translucent pixels are found, break the loop
			if bottom_opaque_pixel is not None and bottom_translucent_pixel is not None:
				break

		if bottom_opaque_pixel is not None and bottom_translucent_pixel is not None:
			break

	return {
		"image_height": image_height,
		"bottom_opaque_pixel": bottom_opaque_pixel,
		"bottom_translucent_pixel": bottom_translucent_pixel
	}

def process_line(line):
	if line == '"': return
	image = line.split(',')[3].replace('"',"")
	image = f'{image}_RHR'
	try:
		if '''catalogRecord.exists":"0"''' in requests.get(f"https://media.restorationhardware.com/is/image/rhis/{image}?req=exists,json").text: return
	except:
		return
	url = f"https://media.restorationhardware.com/is/image/rhis/{image}?wid=1500&fmt=png-alpha"
	result = get_bottom_pixels(url)
	if result == None: return
	try:
		product_to_edge = result['image_height'] - result['bottom_opaque_pixel']
	except TypeError:
		product_to_edge = 0
	try:
		shadow_to_edge = result['image_height'] - result['bottom_translucent_pixel']
	except TypeError:
		shadow_to_edge = 0
	try:
		shadow_length = result['bottom_translucent_pixel'] - result['bottom_opaque_pixel']
	except TypeError:
		shadow_length = 0
	with open(output_file,'a') as output:
		output.write(f"{image},{result['image_height']},{result['bottom_opaque_pixel']},{result['bottom_translucent_pixel']},{product_to_edge},{shadow_to_edge},{shadow_length}\n")



output_file = os.path.expanduser('~/Desktop/shadow_length_test.csv')
try: os.remove(output_file)
except: pass
with open(output_file,'a') as output:
		output.write(f"image,image_height,bottom_opaque_pixel,bottom_translucent_pixel,product_to_edge,shadow_to_edge,shadow_length\n")
def main():
	if len(sys.argv)==1:
		CSV = '/Users/landerson2/Desktop/living.csv'
	else:
		CSV = sys.argv[1]
	with open(CSV, 'r') as csv:
		lines = csv.readlines()
		for line in lines:
			while threading.active_count()>50: continue
			threading.Thread(target = process_line, args = (line,)).start()

if __name__ == '__main__': main()