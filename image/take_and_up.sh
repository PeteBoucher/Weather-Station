
raspistill -vf -hf -o image.jpg
echo "image taken!"
sudo python /home/pi/Weather-Station/image/up_image.py
echo "image uploaded!"
