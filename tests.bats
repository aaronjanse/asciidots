#!/usr/bin/env bats

@test "count to 100" {
  run python3 . ./tests/count_to_100.dots
  [ "$status" -eq 0 ]
  [ "$output" = "$(seq 100)" ]
}

@test "use for in range library" {
  run python3 . ./tests/use_for_in_range.dots
  [ "$status" -eq 0 ]
  [ "$output" = "$(seq 9)" ]
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

@test "factor" {
  result="$(echo 24 | python3 . ./tests/factor.dots)"
  [ "$result" = "$(seq 4)" ]
}

@test "singleton" {
  run python3 . ./tests/singleton.dots
  [ "$status" -eq 0 ]
  [ "$output" = "$(seq 5)" ]
}

@test "singleton in/out" {
  run python3 . ./tests/singleton_2.dots
  [ "$status" -eq 0 ]
  [ "$output" = "$(echo -e "-1\n1")" ]
}

@test "and" {
  run python3 . ./tests/and.dots
  [ "$status" -eq 0 ]
  [ "$output" = "Good" ]
}

@test "timing" {
  run python3 . ./tests/lock.dots
  [ "$status" -eq 0 ]
  [ "$output" = "1" ]
}

@test "ascii input" {
  result=$(echo "END" | python3 . tests/ascii_input.dots)
  [ "$result" = "Success!" ]
}

@test "filter chars" {
  result=$(echo "END" | python3 . tests/filter_chars.dots)
  [ "$result" = "0011" ]
}