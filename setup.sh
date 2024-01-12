apt-get update
apt-get upgrade
apt-get install direnv make python3-pip vim cmake -y

git config --global credential.helper 'cache --timeout=864000'
git config --global user.email 'hyeon95y@gmail.com'
git config --global user.name 'Hyeonwoo Daniel Yoo'

echo 'eval "$(direnv hook bash)"' >> ~/.bashrc
. ~/.bashrc

direnv allow 
