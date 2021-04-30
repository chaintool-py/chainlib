pragma solidity ^0.8.0;

contract Owned {
	address public owner;
	address newOwner;

	constructor() public {
		owner = msg.sender;	
	}

	function transferOwnership(address _newOwner) public returns (bool) {
		require(owner == msg.sender);
		newOwner = _newOwner;
		return true;
	}

	function acceptOwnership() public returns (bool) {
		require(newOwner == msg.sender);
		owner = msg.sender;
		newOwner = address(0);
		return true;
	}

	function takeOwnership(address _ownable) public returns (bool) {
		bool ok;
		bytes memory result;

		(ok, result) = _ownable.call(abi.encodeWithSignature("acceptOwnership()"));
		require(ok, "ERR_ACCEPT");
		return true;
	}
}
