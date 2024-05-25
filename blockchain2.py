from web3 import Web3
from web3.middleware import geth_poa_middleware
import ipfshttpclient2

contract_address = '0x1A41Ffa2eEE3Cf6d4049C699699593d0EedE7e3A'
contract_abi = [
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "_name",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_lastName",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "_idNumber",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "_fileCID",
				"type": "string"
			}
		],
		"name": "addPerson",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_idNumber",
				"type": "uint256"
			},
			{
				"internalType": "bool",
				"name": "state",
				"type": "bool"
			}
		],
		"name": "enableDisablePerson",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "_name",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_lastName",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "_idNumber",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_idNumberNew",
				"type": "uint256"
			}
		],
		"name": "updatePerson",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getNumPersons",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_idNumber",
				"type": "uint256"
			}
		],
		"name": "getPersonByIdNumber",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			},
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_index",
				"type": "uint256"
			}
		],
		"name": "getPersonByIndex",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			},
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "persons",
		"outputs": [
			{
				"internalType": "string",
				"name": "name",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "lastName",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "idNumber",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "fileCID",
				"type": "string"
			},
			{
				"internalType": "bool",
				"name": "isActive",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]


alchemy_url = "https://polygon-amoy.g.alchemy.com/v2/hDOJuTToNZ_KfytNFUNUmu-OvXSROQNg"

# Crear la instancia del contrato
w3 = Web3(Web3.HTTPProvider(alchemy_url))
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Info Metamask
account_address = ''
private_key = ''


# Conexion a nodo IPFS
client = ipfshttpclient2.connect('/ip4/127.0.0.1/tcp/5001/http')