#!/bin/bash

# Exit the script if any command fails
set -e

# Step 1: Update the system and install necessary packages
echo "Updating the system and installing necessary packages..."
sudo apt update
sudo apt install -y python3-pip python3-dev nginx git

# Step 2: Clone the project from GitHub
echo "Cloning the project from GitHub..."
git clone https://github.com/Kev-Cui/IO_group_project_music_recommender.git
cd IO_group_project_music_recommender

# Step 3: Install Python dependencies
echo "Installing Python dependencies..."
pip3 install flask pickle spotipy pandas sklearn

# Step 4: Test the app (optional - uncomment to run this test)
# echo "Testing the application..."
# python3 recommender.py

# Step 5: Install and configure Gunicorn
echo "Installing Gunicorn..."
pip3 install gunicorn

echo "Running Gunicorn..."
# Get the Gunicorn process ID (PID)
GUNICORN_PID=$!

# Emulate waiting for a button press (sleep for 10 seconds)
echo "Simulating button press 'x'... (waiting for 10 seconds)"
sleep 10

# Simulate pressing Ctrl+C by killing the Gunicorn process
echo "Stopping Gunicorn (simulating Ctrl+C)..."
kill $GUNICORN_PID

# Step 6: Configure Nginx as a reverse proxy
EXTERNAL_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
INTERNAL_IP=$(hostname -I | awk '{print $1}')

echo "Configuring Nginx reverse proxy..."
sudo bash -c "cat > /etc/nginx/sites-available/recommender" <<EOL
server {
    listen 80;
    server_name ${EXTERNAL_IP}; # Replace with your server's external IP

    root /var/www/html;

    location / {
        proxy_pass http://${INTERNAL_IP}:8000; # Internal IP of the server
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL

# Enable the Nginx configuration
echo "Enabling the Nginx configuration..."
sudo ln -s /etc/nginx/sites-available/recommender /etc/nginx/sites-enabled

# Test the Nginx configuration
echo "Testing Nginx configuration..."
sudo nginx -t

# Restart Nginx
echo "Restarting Nginx..."
sudo systemctl restart nginx

# Step 7: Run the Flask app using Gunicorn
echo "Starting Gunicorn server with 3 workers..."
gunicorn --workers 3 --bind 0.0.0.0:8000 recommender:app &
