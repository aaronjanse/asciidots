#!/usr/bin/env bats

@test "count to 100" {
  run python3 . ./tests/count_to_100.dots
  [ "$status" -eq 0 ]
  [ "$output" = "$(seq 100)" ]
}

@test "use for in range library" {
  run python3 . ./tests/use_for_in_range.dots
  [ "$status" -eq 0 ]
  [ "$output" = "$(seq 10)" ]
}

@test "use warps" {
  run python3 . ./tests/warps.dots
  [ "$status" -eq 0 ]
  [ "$output" = "3" ]
}

@test "three" {
  run python3 . ./tests/three.dots
  [ "$status" -eq 0 ]
  [ "$output" = "3" ]
}

@test "quine" {
  run python3 . ./tests/quine.dots
  [ "$status" -eq 0 ]
  [ "$(echo $output)" = "$(cat ./tests/quine.dots)" ]
}
