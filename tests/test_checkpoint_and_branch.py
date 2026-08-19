"""Regression coverage for Checkpoint/branch_from (ADR 0001/0002).

Runs against the real Dymola-family FMU, matching the project's existing
practice of validating this mechanism empirically rather than through mocks.
"""

from buildyn.checkpoint import Checkpoint

OBSERVABLE = "thermalZone.TAir"

# ADR 0001 finding 4: freshly-transplanted branches can show a transient,
# self-healing ~1-3 mK deviation from a continuously-warm source near a
# solver/table event. This tolerance follows directly from that finding.
BRANCH_NOISE_TOLERANCE = 0.01


def test_checkpoint_carries_the_time_it_was_taken_at(make_dymola_fmu):
    fmu = make_dymola_fmu()

    fmu.step_fmu(900)
    fmu.step_fmu(900)

    checkpoint = fmu.get_checkpoint()

    assert isinstance(checkpoint, Checkpoint)
    assert checkpoint.time == fmu.time == 1800


def test_set_checkpoint_restores_state_and_resyncs_time(make_dymola_fmu):
    fmu = make_dymola_fmu()

    fmu.step_fmu(900)
    checkpoint = fmu.get_checkpoint()
    value_at_checkpoint = fmu.get_variable(OBSERVABLE)

    fmu.step_fmu(900)
    fmu.step_fmu(900)
    assert fmu.time != checkpoint.time

    fmu.set_checkpoint(checkpoint)

    assert fmu.time == checkpoint.time
    assert fmu.get_variable(OBSERVABLE) == value_at_checkpoint


def test_set_checkpoint_rejects_a_checkpoint_from_a_different_instance(make_dymola_fmu):
    source = make_dymola_fmu()
    source.step_fmu(900)
    checkpoint = source.get_checkpoint()

    # A target that has already gone through its own initialization (i.e. is
    # "ready") is rejected too - set_checkpoint's guard is unconditional.
    target = make_dymola_fmu()
    target.step_fmu(900)

    try:
        target.set_checkpoint(checkpoint)
        assert False, "expected set_checkpoint to reject a foreign checkpoint"
    except ValueError:
        pass


def test_branch_from_transplants_source_state_onto_a_target_instance(make_dymola_fmu):
    source = make_dymola_fmu()
    target = make_dymola_fmu()

    for _ in range(4):
        source.step_fmu(900)

    checkpoint = source.get_checkpoint()

    target.branch_from(checkpoint)

    assert target.time == checkpoint.time == source.time
    assert target.get_variable(OBSERVABLE) == source.get_variable(OBSERVABLE)


def test_branch_tracks_source_continuation_within_documented_tolerance(make_dymola_fmu):
    source = make_dymola_fmu()
    target = make_dymola_fmu()

    for _ in range(4):
        source.step_fmu(900)

    target.branch_from(source.get_checkpoint())

    for _ in range(4):
        source.step_fmu(900)
        target.step_fmu(900)

    assert target.time == source.time
    assert abs(target.get_variable(OBSERVABLE) - source.get_variable(OBSERVABLE)) < BRANCH_NOISE_TOLERANCE


def test_branch_pool_is_reset_and_reused_across_repeated_decision_cycles(make_dymola_fmu):
    # 25 cycles to match the scale of ADR 0001 / Experiment D: the ~mK
    # transient in finding 4 only showed up at cycles 17-19 of a 25-cycle
    # run, so a shorter loop can't regress-test that window.
    source = make_dymola_fmu()
    branch = make_dymola_fmu()

    for cycle in range(25):
        source.step_fmu(900)
        checkpoint = source.get_checkpoint()
        source_snapshot = (source.time, source.get_variable(OBSERVABLE))

        branch.branch_from(checkpoint)
        assert branch.time == checkpoint.time
        assert abs(branch.get_variable(OBSERVABLE) - source_snapshot[1]) < BRANCH_NOISE_TOLERANCE

        branch.step_fmu(900)

        # Isolation (ADR 0001 finding 6 / Experiment D3): reusing/stepping the
        # branch must not touch source, which hasn't been stepped again yet.
        assert (source.time, source.get_variable(OBSERVABLE)) == source_snapshot

        source.step_fmu(900)
        assert abs(branch.get_variable(OBSERVABLE) - source.get_variable(OBSERVABLE)) < BRANCH_NOISE_TOLERANCE


def test_branch_from_resyncs_time_from_the_checkpoint_not_the_caller(make_dymola_fmu, dymola_params):
    source = make_dymola_fmu()

    for _ in range(3):
        source.step_fmu(900)

    checkpoint = source.get_checkpoint()

    target = make_dymola_fmu()
    target.branch_from(checkpoint, params=dymola_params, start_time=0)

    assert target.time == checkpoint.time
    assert target.time != 0
    assert target.get_variable(OBSERVABLE) == source.get_variable(OBSERVABLE)


def test_multiple_branches_share_a_checkpoint_without_affecting_main_or_each_other(make_dymola_fmu):
    main = make_dymola_fmu()
    branches = [make_dymola_fmu() for _ in range(3)]

    for _ in range(3):
        main.step_fmu(900)

    checkpoint = main.get_checkpoint()
    main_value_at_checkpoint = main.get_variable(OBSERVABLE)

    for branch in branches:
        branch.branch_from(checkpoint)

    for branch in branches:
        assert branch.time == checkpoint.time
        assert abs(branch.get_variable(OBSERVABLE) - main_value_at_checkpoint) < BRANCH_NOISE_TOLERANCE

    for branch in branches:
        branch.step_fmu(900)

    # Stepping/resetting the branches must not alias back onto main.
    assert main.time == checkpoint.time
    assert main.get_variable(OBSERVABLE) == main_value_at_checkpoint


def test_openmodelica_fmu_reports_state_transplant_as_unsupported(openmodelica_fmu_path):
    from fmpy import read_model_description

    model_description = read_model_description(openmodelica_fmu_path)

    assert model_description.coSimulation.canGetAndSetFMUstate is False


def test_openmodelica_fmu_can_be_instantiated_and_stepped(make_openmodelica_fmu):
    fmu = make_openmodelica_fmu()

    fmu.step_fmu(900)

    assert fmu.time == 900
    assert isinstance(fmu.get_variable(OBSERVABLE), float)


def test_branch_from_raises_clearly_when_state_transplant_is_unsupported(make_dymola_fmu, make_openmodelica_fmu):
    source = make_dymola_fmu()
    source.step_fmu(900)
    checkpoint = source.get_checkpoint()

    unsupported = make_openmodelica_fmu()

    try:
        unsupported.branch_from(checkpoint)
        assert False, "expected branch_from to raise on an unsupported FMU"
    except RuntimeError:
        pass


def test_get_checkpoint_raises_clearly_when_state_transplant_is_unsupported(make_openmodelica_fmu):
    fmu = make_openmodelica_fmu()

    try:
        fmu.get_checkpoint()
        assert False, "expected get_checkpoint to raise on an unsupported FMU"
    except RuntimeError:
        pass
