# SWIM - Docker

Run docker container (add port 4242 for external adaptation control)


```powershell
(docker container rm swim)
docker run -d -p 5901:5901 -p 6901:6901 -p 4242:4242 --name swim gabrielmoreno/swim
```

Go to:
http://localhost:6901
pw: vncpassword

Open Terminal Emulator

Inside container - start simulation:
```powershell
cd ~/seams-swim/swim/simulations/swim/
./run.sh sim 1
```

Alternatively without web application over terminal
```powershell
(docker ps) // show name of container
docker exec -it [NAME] sh
```