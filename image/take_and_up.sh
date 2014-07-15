
raspistill -vf -hf -o image.jpg
echo "image taken!"
sudo python /home/pi/weatherStation/image/up_image.py
echo "image uploaded!"
