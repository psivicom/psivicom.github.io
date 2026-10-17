package scheduler

import "fmt"

type PSVCInstruction struct {
	OpCode uint8
	Data   uint64
}

func ExecutePSVC(instr PSVCInstruction) error {
	switch instr.OpCode {
	case 0x01:
		return nil
	default:
		return fmt.Errorf("invalid psvc opcode: %d", instr.OpCode)
	}
}