// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

contract PersonInfo {
    struct Person {
        string name;
        string lastName;
        uint idNumber;
        string fileCID;
        bool isActive;
    }

    Person[] public persons;
    mapping(uint => uint) idToPersonIndex; // Nuevo mapeo

    constructor() {
            persons.push(Person('none', 'none', 0, 'none', false));
            
        } 

    // Función para añadir una persona (modificada para actualizar el mapeo)
    function addPerson(string memory _name, string memory _lastName, uint _idNumber, string memory _fileCID) public {
        persons.push(Person(_name, _lastName, _idNumber, _fileCID, true));
        uint index = persons.length - 1;
        idToPersonIndex[_idNumber] = index; // Actualiza el mapeo con el nuevo índice
        
    }

    // Función para obtener la información de una persona por su número de identificación
    function getPersonByIdNumber(uint _idNumber) public view returns (string memory, string memory, uint, string memory, bool) {
        uint index = idToPersonIndex[_idNumber];
        require(index > 0, "Person does not exist."); // Verifica si la persona existe
        Person memory p = persons[index];
        return (p.name, p.lastName, p.idNumber, p.fileCID, p.isActive);
        
    }

    // Función para obtener la información de una persona por Index del array
    function getPersonByIndex(uint _index) public view returns (string memory, string memory, uint, string memory, bool) {
        return (persons[_index].name, persons[_index].lastName, persons[_index].idNumber, persons[_index].fileCID, persons[_index].isActive);
    }

    function getNumPersons() public view returns (uint){
        uint index = persons.length - 1;
        return (index);
    }

    function updatePerson(string memory _name, string memory _lastName, uint _idNumber, uint _idNumberNew) public {
        uint index = idToPersonIndex[_idNumber];
        persons[index].name = _name;
        persons[index].lastName = _lastName;
        persons[index].idNumber = _idNumberNew;
        idToPersonIndex[_idNumberNew] = index; // Actualiza el mapeo con el nuevo índice
        if (_idNumber != _idNumberNew) {
            idToPersonIndex[_idNumber] = 0;
        }
    }

    function enableDisablePerson(uint _idNumber, bool state) public {
        uint index = idToPersonIndex[_idNumber];
        if (state == true) {
            persons[index].isActive = true;
        }
        if (state == false) {
            persons[index].isActive = false;
        }
    }
}