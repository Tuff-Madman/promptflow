$first_commit = 'yigao/enforcer_fix' # github.sha
$diff_commit = 'main'
$github_repository = 'microsoft/promptflow'
$first_commit_hash = 'a1bfd6865ac8a52a0af9f8a3c723055e287f9780' #git rev-parse $first_commit


function get_diffs() {

    $need_to_check = New-Object System.Collections.Generic.HashSet[string]
    git diff --name-only $first_commit $diff_commit | ForEach-Object {
        if ($_.Contains("src/promptflow")) {
            $need_to_check.Add("sdk_cli")
        }
    }

    $failed_reason =  ""
    $failedCount = 3

    for ($i = 0; $i -lt $failedCount; $i++) {
        #Start-Sleep -Seconds 20
        
        $pipelines = @{
            "executor_e2e_tests" = 0;
            "executor_unit_tests" = 0;
            "sdk_cli_tests" = 0;
            "sdk_cli_global_config_tests" = 0;
            "sdk_pfs_e2e_test" = 0;
            "sdk_cli_azure_test" = 0;
        }
        $pipelines_count = @{
            "executor_e2e_tests" = 0;
            "executor_unit_tests" = 0;
            "sdk_cli_tests" = 0;
            "sdk_cli_global_config_tests" = 0;
            "sdk_pfs_e2e_test" = 0;
            "sdk_cli_azure_test" = 0;
        }
        
        foreach ($item in $need_to_check) {
            if ($item -eq "sdk_cli") {
                $pipelines.sdk_cli_tests = 2
                $pipelines.sdk_cli_global_config_tests = 1
                $pipelines.sdk_cli_azure_test = 2
                $pipelines.sdk_pfs_e2e_test = 2
            }
        }

        # Get pipeline status.
        $valid_status_array = $(gh api /repos/$github_repository/commits/$first_commit_hash/check-runs) `
        | ConvertFrom-Json `
        | Select-Object -ExpandProperty check_runs `
        | Where-Object {
            foreach ($key in $pipelines.Keys) {
                $value = $pipelines[$key]
                if ($value -eq 0) {
                    continue
                }
                if ($_.name.Contains($key)) {
                    $pipelines_count[$key] += 1
                    return $true
                }
            }
            return $false
        }
        

        # Get pipeline conclusion. count should match.

        foreach ($key in $pipelines.Keys) {
            if ($pipelines_count[$key] -lt $pipelines[$key]) {
                $failed_reason = "Not all pipelines are triggered."
            }
        }
        if ($failed_reason -ne "") {
            Write-Host $failed_reason
            Write-Host $pipelines_count
            continue
        }
        $pipelines_success_count = @{
            "executor_e2e_tests" = 0;
            "executor_unit_tests" = 0;
            "sdk_cli_tests" = 0;
            "sdk_cli_global_config_tests" = 0;
            "sdk_pfs_e2e_test" = 0;
            "sdk_cli_azure_test" = 0;
        }

        $valid_status_array `
        | ForEach-Object {
            foreach ($key in $pipelines.Keys) {
                $value = $pipelines[$key]
                if ($value -eq 0) {
                    continue
                }
                if ($_.name.Contains($key)) {
                    if ($_.conclusion -ieq "success") {
                        $pipelines_success_count[$pipelines.Keys[$j]] += 1
                    } elseif ($_.conclusion -ieq "failure") {
                        $failed_reason = "Required pipelines are not successful."
                    } else {
                        $failed_reason = "Required pipelines are not finished."
                    }
                }
            }
        }
        if ($failed_reason.Contains("not successful")) {
            Write-Host $failed_reason
            break
        } elseif ($failed_reason.Contains("not successful")) {
            Write-Host $failed_reason
            continue
        } else {
            Write-Host "All required pipelines are successful."
            break
        }
    }
}

get_diffs