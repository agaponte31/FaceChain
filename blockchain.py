from web3 import Web3
from web3.middleware import geth_poa_middleware
import ipfshttpclient2

contract_address = '0x6f676330f211170864FC18030e211d44290863cc'
contract_abi = [
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "_name",
				"type": "bytes32"
			},
			{
				"internalType": "bytes32",
				"name": "_lastName",
				"type": "bytes32"
			},
			{
				"internalType": "bytes32",
				"name": "_idNumber",
				"type": "bytes32"
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
				"internalType": "bytes32",
				"name": "_idNumber",
				"type": "bytes32"
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
				"internalType": "bytes32",
				"name": "_name",
				"type": "bytes32"
			},
			{
				"internalType": "bytes32",
				"name": "_lastName",
				"type": "bytes32"
			},
			{
				"internalType": "bytes32",
				"name": "_idNumber",
				"type": "bytes32"
			},
			{
				"internalType": "bytes32",
				"name": "_idNumberNew",
				"type": "bytes32"
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
				"internalType": "bytes32",
				"name": "_idNumber",
				"type": "bytes32"
			}
		],
		"name": "getPersonByIdNumber",
		"outputs": [
			{
				"internalType": "bytes32",
				"name": "",
				"type": "bytes32"
			},
			{
				"internalType": "bytes32",
				"name": "",
				"type": "bytes32"
			},
			{
				"internalType": "bytes32",
				"name": "",
				"type": "bytes32"
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
				"internalType": "bytes32",
				"name": "",
				"type": "bytes32"
			},
			{
				"internalType": "bytes32",
				"name": "",
				"type": "bytes32"
			},
			{
				"internalType": "bytes32",
				"name": "",
				"type": "bytes32"
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
				"internalType": "bytes32",
				"name": "name",
				"type": "bytes32"
			},
			{
				"internalType": "bytes32",
				"name": "lastName",
				"type": "bytes32"
			},
			{
				"internalType": "bytes32",
				"name": "idNumber",
				"type": "bytes32"
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


alchemy_url = "https://eth-sepolia.g.alchemy.com/v2/UYChG3J2Qj8ILzIFMH9BEtqRFoLRk5Ee"

# Crear la instancia del contrato
w3 = Web3(Web3.HTTPProvider(alchemy_url))
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Info Metamask
account_address = ''
private_key = ''


# Conexion a nodo IPFS
client = ipfshttpclient2.connect('/ip4/127.0.0.1/tcp/5001/http')