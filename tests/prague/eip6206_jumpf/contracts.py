"""
EOF V1 Code Validation tests
"""

from typing import List

from ethereum_test_tools import EOFException
from ethereum_test_tools.eof.v1 import Container, Section
from ethereum_test_tools.eof.v1.constants import NON_RETURNING_SECTION
from ethereum_test_tools.vm.opcode import Opcodes as Op


def quick_code(code, inputs=0, outputs=NON_RETURNING_SECTION, height=0):
    """A sorter way to write code with section 0 defaults"""
    return Section.Code(
        code=code, code_inputs=inputs, code_outputs=outputs, max_stack_height=height
    )


def container_name(c: Container):
    """
    Return the name of the container for use in pytest ids.
    """
    if hasattr(c, "name"):
        return c.name
    else:
        return c.__class__.__name__


def generate_jumpf_target_rules():
    """
    Generate tests for JUMPF where we are testing the validity of the JUNMPF target.
    We are not testing stack so a lot of the logic is to get correct stack values.
    """
    valid = []
    invalid = []
    for current_outputs in [NON_RETURNING_SECTION, 0, 2, 4]:
        current_non_returning = current_outputs == NON_RETURNING_SECTION
        current_height = 0 if current_non_returning else current_outputs
        for target_outputs in [NON_RETURNING_SECTION, 0, 2, 4]:
            target_non_returning = target_outputs == NON_RETURNING_SECTION
            target_height = 0 if target_non_returning else target_outputs
            delta = (
                0
                if target_non_returning or current_non_returning
                else target_outputs - current_height
            )
            current_extra_push = max(0, current_height - target_height)
            current_section = Section.Code(
                code=Op.PUSH0 * (current_height)
                + Op.CALLDATALOAD(0)
                + Op.RJUMPI[1]
                + (Op.STOP if current_non_returning else Op.RETF)
                + Op.PUSH0 * current_extra_push
                + Op.JUMPF[2],
                code_inputs=0,
                code_outputs=current_outputs,
                max_stack_height=current_height + max(1, current_extra_push),
            )
            target_section = Section.Code(
                code=((Op.PUSH0 * delta) if delta >= 0 else (Op.POP * -delta))
                + Op.CALLF[3]
                + (Op.STOP if target_non_returning else Op.RETF),
                code_inputs=current_height,
                code_outputs=target_outputs,
                max_stack_height=max(current_height, current_height + delta),
            )

            container = Container(
                name="target_co-%s_to-%s"
                % (
                    "N" if current_non_returning else current_outputs,
                    "N" if target_non_returning else target_outputs,
                ),
                sections=[
                    quick_code(Op.JUMPF[1], height=0 if current_non_returning else current_height)
                    if current_non_returning
                    else quick_code(
                        Op.CALLF[1](0, 0) + Op.STOP,
                        height=0 if current_non_returning else 2 + current_outputs,
                    ),
                    current_section,
                    target_section,
                    quick_code(Op.SSTORE(0, 1) + Op.RETF, outputs=0, height=2),
                ],
            )

            # now sort validity...
            if target_non_returning:
                valid.append(container)
            elif current_non_returning or current_outputs < target_outputs:
                # both as non-returning handled above
                container.validity_error = EOFException.UNDEFINED_EXCEPTION
                invalid.append(container)
            else:
                # both are returning, and current >= target
                valid.append(container)
    return (valid, invalid)


def generate_jumpf_stack_returning_rules():
    """
    Generate tests for JUMPF where we are testing the stack rules.  Returning section cases
    """
    valid = []
    invalid = []
    for current_outputs in [0, 2, 4]:
        for target_outputs in [x for x in [0, 2, 4] if x <= current_outputs]:
            for target_inputs in [0, 2, 4]:
                for stack_diff in [-1, 0, 1] if target_inputs > 0 else [0, 1]:
                    target_delta = target_outputs - target_inputs
                    container = Container(
                        name="stack-retuning_co-%d_to-%d_ti-%d_diff-%d"
                        % (current_outputs, target_outputs, target_inputs, stack_diff),
                        sections=[
                            quick_code(
                                Op.CALLF[1] + Op.SSTORE(0, 1) + Op.STOP, height=2 + current_outputs
                            ),
                            quick_code(
                                Op.PUSH0 * max(0, target_inputs + stack_diff) + Op.JUMPF[2],
                                outputs=current_outputs,
                                height=target_inputs,
                            ),
                            quick_code(
                                (
                                    Op.POP * -target_delta
                                    if target_delta < 0
                                    else Op.PUSH0 * target_delta
                                )
                                + Op.RETF,
                                inputs=target_inputs,
                                outputs=target_outputs,
                                height=max(target_inputs, target_outputs),
                            ),
                        ],
                    )

                    if stack_diff == current_outputs - target_outputs:
                        valid.append(container)
                    else:
                        container.validity_error = EOFException.UNDEFINED_EXCEPTION
                        invalid.append(container)

    return (valid, invalid)


def generate_jumpf_stack_non_returning_rules():
    """
    Generate tests for JUMPF where we are testing the stack rules.  Non-returning section cases.
    """
    valid = []
    invalid = []
    for stack_height in [0, 2, 4]:
        for target_inputs in [0, 2, 4]:
            container = Container(
                name="stack-non-retuning_h-%d_ti-%d" % (stack_height, target_inputs),
                sections=[
                    quick_code(Op.JUMPF[1]),
                    quick_code(
                        Op.PUSH0 * stack_height + Op.JUMPF[2],
                        height=stack_height,
                    ),
                    quick_code(
                        Op.POP * target_inputs + Op.SSTORE(0, 1) + Op.STOP,
                        inputs=target_inputs,
                        height=max(2, target_inputs),
                    ),
                ],
            )

            if stack_height >= target_inputs:
                valid.append(container)
            else:
                container.validity_error = EOFException.UNDEFINED_EXCEPTION
                invalid.append(container)

    return (valid, invalid)


jump_forward = Container(
    name="jump_forward",
    sections=[quick_code(Op.JUMPF[1]), quick_code(Op.SSTORE(0, 1) + Op.STOP, height=2)],
)
jump_backward = Container(
    name="jump_backward",
    sections=[
        quick_code(Op.CALLF[2] + Op.SSTORE(0, 1) + Op.STOP, height=2),
        quick_code(Op.RETF, outputs=0),
        quick_code(Op.JUMPF[1], outputs=0),
    ],
)
jump_to_self = Container(
    name="jump_to_self",
    sections=[
        quick_code(
            Op.SLOAD(0) + Op.ISZERO + Op.RJUMPI[1] + Op.STOP + Op.SSTORE(0, 1) + Op.JUMPF[0],
            height=2,
        )
    ],
)
jump_too_large = Container(
    name="jump_too_large",
    sections=[quick_code(Op.JUMPF[1025])],
    validity_error=EOFException.UNDEFINED_EXCEPTION,
)
jump_way_too_large = Container(
    name="jump_way_too_large",
    sections=[quick_code(Op.JUMPF[0xFFFF])],
    validity_error=EOFException.UNDEFINED_EXCEPTION,
)
jump_non_existent_section = Container(
    name="jump_non_existent_section",
    sections=[quick_code(Op.JUMPF[5])],
    validity_error=EOFException.UNDEFINED_EXCEPTION,
)
callf_non_returning = Container(
    name="callf_non_returning",
    sections=[quick_code(Op.CALLF[1]), quick_code(Op.STOP, outputs=NON_RETURNING_SECTION)],
    validity_error=EOFException.UNDEFINED_EXCEPTION,
)


jumpf_targets = generate_jumpf_target_rules()
jumpf_stack_returning = generate_jumpf_stack_returning_rules()
jumpf_stack_non_returning = generate_jumpf_stack_non_returning_rules()

VALID: List[Container] = [
    jump_forward,
    jump_backward,
    jump_to_self,
    *jumpf_targets[0],
    *jumpf_stack_returning[0],
    *jumpf_stack_non_returning[0],
]

INVALID: List[Container] = [
    jump_too_large,
    jump_too_large,
    jump_non_existent_section,
    callf_non_returning,
    *jumpf_targets[1],
    *jumpf_stack_returning[1],
    *jumpf_stack_non_returning[1],
]
