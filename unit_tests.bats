#!/usr/bin/env bats

@test "count to 100" {
  run python3 . ./tests/count_to_100.fry
  [ "$status" -eq 0 ]
  [ "$output" = "$(seq 100)" ]
}

@test "use for in range library" {
  run python3 . ./tests/cuse_for_in_range.fry
  [ "$status" -eq 0 ]
  [ "$output" = "$(seq 10)" ]
}

@test "use warps" {
  run python3 . ./tests/warps.fry
  [ "$status" -eq 0 ]
  [ "$output" = "3" ]
}
