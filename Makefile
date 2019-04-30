#
# written by junying,
# 2019-04-16
#

# basic commands
deps:
	@pip install -r requirements.txt

retart: stop start

start:
	@nohup /usr/bin/python  server.py &  > /dev/null

stop: clean
	@pkill -9 python

clean:
	@find -name nohup.out -exec rm -f {} \;
	@find -name "*.pyc" -exec rm -f {} \;
	@find -name __pycache__ | xargs rm -rf 
	@find -name .cache | xargs rm -rf 
	
check:
	@ps axu | grep server.py

pytest:
	@py.test

zip:
	@find ../ -name rpc.tar.gz -exec rm -f {} \;
	@tar pcvf ../rpc.tar.gz ../pyrpc --exclude=../pyrpc/README.md --exclude=../pyrpc/Makefile --exclude=../pyrpc/.travis.yml --exclude=../pyrpc/.vscode

replace:
	@wormhole send ../rpc.tar.gz

update: zip replace

# auto generate
autogen: genowt genup

genowt:
	@if [ -d "owt" ]; then rm -rf owt; fi
	@cp -rf eth owt
	@find ./owt -type f -exec sed -i -e 's/EthereumProxy/OrientWaltProxy/g' {} \;
	@find ./owt -type f -exec sed -i -e 's/t_ethereum_accounts/t_orientwalt_accounts/g' {} \;
	@find ./owt -type f -exec sed -i -e 's/eth\./owt\./g' {} \;
	@find ./owt -type f -exec sed -i -e 's/ethereum/orientwalt/g' {} \;
	@find ./owt -type f -exec sed -i -e 's/eth_/owt_/g' {} \;
	@find ./owt -type f -exec sed -i -e 's/ETH/OWT/g' {} \;
	@find ./owt -type f -exec sed -i -e 's/orientwalt/ethereum/g' {} \;

genup:
	@if [ -d "up" ]; then rm -rf up; fi
	@cp -rf eth up
	@find ./up -type f -exec sed -i -e 's/EthereumProxy/UnitedProneProxy/g' {} \;
	@find ./up -type f -exec sed -i -e 's/t_ethereum_accounts/t_unitedprone_accounts/g' {} \;
	@find ./up -type f -exec sed -i -e 's/eth\./up\./g' {} \;
	@find ./up -type f -exec sed -i -e 's/ethereum/unitedprone/g' {} \;
	@find ./up -type f -exec sed -i -e 's/eth_/up_/g' {} \;
	@find ./up -type f -exec sed -i -e 's/ETH/UP/g' {} \;
	@find ./up -type f -exec sed -i -e 's/unitedprone/ethereum/g' {} \;
