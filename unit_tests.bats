#!/usr/bin/env bats

@test "count to 100" {
  run python . ./tests/count_to_100.dots
  [ "$status" -eq 0 ]
  [ "$output" = "$(seq 100)" ]
}

@test "use for in range library" {
  run python . ./tests/use_for_in_range.dots
  [ "$status" -eq 0 ]
  [ "$output" = "$(seq 10)" ]
}

@test "use warps" {
  run python . ./tests/warps.dots
  [ "$status" -eq 0 ]
  [ "$output" = "3" ]
}

@test "three" {
  run python . ./tests/three.dots
  [ "$status" -eq 0 ]
  [ "$output" = "3" ]
}

@test "quine" {
  run python . ./tests/quine.dots
  [ "$status" -eq 0 ]
  [ "$(echo $output)" = "$(cat ./tests/quine.dots)" ]
}

@test "factor" {
  result="$(echo 24 | python . ./tests/factor.dots)"
  [ "$result" = "$(seq 4)" ]
}

@test "singleton" {
  run python . ./tests/singleton.dots
  [ "$status" -eq 0 ]
  [ "$output" = "$(seq 5)" ]
}

@test "and" {
  run python . ./tests/and.dots
  [ "$status" -eq 0 ]
  [ "$output" = "Good" ]
}
