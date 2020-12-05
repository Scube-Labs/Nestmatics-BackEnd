rm -r dist

rm dist.zip

curl -s https://api.github.com/repos/Scube-Labs/Nestmatics-Frontend/releases/latest | grep "browser_download_url.*zip" | cut -d : -f 2,3 | tr -d \" | wget -qi -

unzip dist.zip
