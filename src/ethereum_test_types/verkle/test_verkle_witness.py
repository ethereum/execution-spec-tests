"""
Test suite for the verkle witness.
"""

import pytest

from ethereum_test_types.verkle import IpaProof, StateDiff, SuffixStateDiff, VerkleProof, Witness


@pytest.fixture
def ipa_proof_data():
    """
    Valid verkle proof data.
    """
    return {
        "cl": [
            "0x64b54668075852328d955f6f2336a9a06defa7a8b49718a013a3849212988c5a",
            "0x360403c03f7e21825e7ff76be9d5b6067032230c6f91c618298796bfc47a0c11",
            "0x064fbaf6f5ff7e7d126cec7665789a0a62f43b68f2e6e8167b7cca82455ab6c7",
            "0x3b02cb202ecbb384215e8ad74a9be278fb762f667bade979f8f9a39088918af0",
            "0x57fa59af60061d72fc92e4264bad153885c0d06991dc6736e4f4b081326a1cdc",
            "0x24dd138cd53f71e075a07fe4532168de6d6061bfe491e7768bcc1d7713bc3bcb",
            "0x5da706b290cee4ca425d13c49bbe4da202de79010051d9d3b1c052142fb2e7aa",
            "0x238f6f59bc86c521e6fce993f84f4b666fcf25248aee148d898a9e614c3fee13",
        ],
        "cr": [
            "0x2aa66cbd97293e3524945cb9660c97a42b71e29718cdda0841fcf18636b57a1b",
            "0x73e20d72f31583e21e5bb204d262a737d190d993af234b3cb4b6ecdddc49b61b",
            "0x4b8602d3f96d61c74dc19f771c907224b086086e0207fbe2e24d511627102ba4",
            "0x446ac6121c2fbc0a4cc656121c160f049a07f0d63307aae23815c1a7ec80cfdf",
            "0x6d5a3fbd3356e5df2d93052cc9e402dab4ef5014af9b35fc32977c584e7613bc",
            "0x4399dfaf28ee7a4fda83a04ea189201b0f63b897b74f5d5dc51535ff23d48124",
            "0x4441409deb28990e3b51235f7ea131a2772237167fe266fbcd0ba19f422364e3",
            "0x39966d71a2cf09311940c164ef8e5f37e09a64226535c4aeaf26944f3f5f1b2e",
        ],
        "finalEvaluation": "0x0773f10637892f75d48ef0ed3e421b6e435220d17a99ec2914af567d46c70988",
    }


def test_ipa_proof_validation(ipa_proof_data):
    """
    Performs basic IPA proof format validation.
    """
    ipa_proof = IpaProof(**ipa_proof_data)
    assert ipa_proof.cl[0] == 0x64B54668075852328D955F6F2336A9A06DEFA7A8B49718A013A3849212988C5A
    assert ipa_proof.cr[0] == 0x2AA66CBD97293E3524945CB9660C97A42B71E29718CDDA0841FCF18636B57A1B
    assert ipa_proof.final_evaluation == (
        0x0773F10637892F75D48EF0ED3E421B6E435220D17A99EC2914AF567D46C70988
    )


@pytest.fixture
def verkle_proof_data(ipa_proof_data):
    """
    Valid verkle proof data.
    """
    return {
        "otherStems": [
            "0x5b5fdfedd6a0e932da408ac7d772a36513d1eee9b9926e52620c43a433aad7",
            "0x5b5fdfedd6a0e932da408ac7d772a36513d1eee9b9926e52620c43a433aad7",
        ],
        "depthExtensionPresent": "0x0a",
        "commitmentsByPath": [
            "0x73bd3673ee58f638feb0e21ba8b0cfeadbc9b280716915338b4f46556aa68226",
            "0x12fe9ad68c17edfed0861a1b19f0bc178836f56abf3514742cb2d4645b35ba92",
        ],
        "d": "0x392ac76ac887f79c7c6fd5fd26ec9cfd44664a69aa5075477cbdfdcb522d2a7a",
        "ipaProof": ipa_proof_data,
    }


def test_verkle_proof_validation(verkle_proof_data):
    """
    Performs basic verkle proof format validation.
    """
    verkle_proof = VerkleProof(**verkle_proof_data)
    assert verkle_proof.other_stems[0] == (
        0x5B5FDFEDD6A0E932DA408AC7D772A36513D1EEE9B9926E52620C43A433AAD7
    )
    assert verkle_proof.depth_extension_present == 0x0A
    assert (
        verkle_proof.commitments_by_path[0]
        == 0x73BD3673EE58F638FEB0E21BA8B0CFEADBC9B280716915338B4F46556AA68226
    )
    assert (
        verkle_proof.commitments_by_path[1]
        == 0x12FE9AD68C17EDFED0861A1B19F0BC178836F56ABF3514742CB2D4645B35BA92
    )
    assert verkle_proof.d == 0x392AC76AC887F79C7C6FD5FD26EC9CFD44664A69AA5075477CBDFDCB522D2A7A
    assert verkle_proof.ipa_proof.final_evaluation == (
        0x0773F10637892F75D48EF0ED3E421B6E435220D17A99EC2914AF567D46C70988
    )


@pytest.fixture
def suffix_diff_data():
    """
    Valid verkle suffix diff data.
    """
    return {
        "suffix": 66,
        "currentValue": "0x647ed3c87a4f764421ea2f5bfc73195812f6b7dd15ac2b8d295730c1dede1edf",
        "newValue": None,
    }


def test_suffix_diff_validation(suffix_diff_data):
    """
    Performs basic suffix diff format validation.
    """
    suffix_diff = SuffixStateDiff(**suffix_diff_data)
    assert suffix_diff.suffix == 66
    assert suffix_diff.current_value == (
        0x647ED3C87A4F764421EA2F5BFC73195812F6B7DD15AC2B8D295730C1DEDE1EDF
    )
    assert suffix_diff.new_value is None


@pytest.fixture
def state_diff_data(suffix_diff_data):
    """
    Valid verkle state diff data.
    """
    return [
        {
            "stem": "0x5b5fdfedd6a0e932da408ac7d772a36513d1eee9b9926e52620c43a433aad7",
            "suffixDiffs": [suffix_diff_data],
        }
    ]


def test_state_diff_validation(state_diff_data):
    """
    Performs basic state diff format validation.
    """
    state_diff = StateDiff(state_diff_data)
    assert state_diff.root[0].stem == (
        0x5B5FDFEDD6A0E932DA408AC7D772A36513D1EEE9B9926E52620C43A433AAD7
    )
    assert state_diff.root[0].suffix_diffs[0].suffix == 66
    assert state_diff.root[0].suffix_diffs[0].current_value == (
        0x647ED3C87A4F764421EA2F5BFC73195812F6B7DD15AC2B8D295730C1DEDE1EDF
    )
    assert state_diff.root[0].suffix_diffs[0].new_value is None


@pytest.fixture
def witness_data(state_diff_data, verkle_proof_data):
    """
    Valid verkle witness data.
    """
    return {
        "stateDiff": state_diff_data,
        "verkleProof": verkle_proof_data,
    }


def test_witness_validation(witness_data):
    """
    Performs basic witness format validation.
    """
    witness = Witness(**witness_data)
    assert witness.verkle_proof.depth_extension_present == 0x0A
    assert (
        witness.verkle_proof.commitments_by_path[0]
        == 0x73BD3673EE58F638FEB0E21BA8B0CFEADBC9B280716915338B4F46556AA68226
    )
    assert (
        witness.state_diff.root[0].suffix_diffs[0].current_value
        == 0x647ED3C87A4F764421EA2F5BFC73195812F6B7DD15AC2B8D295730C1DEDE1EDF
    )
    assert witness.state_diff.root[0].suffix_diffs[0].new_value is None
