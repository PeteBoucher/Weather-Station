
raspistill -vf -hf -o image.jpg
echo "image taken!"
sudo python up_image.py
echo "image uploaded!"
