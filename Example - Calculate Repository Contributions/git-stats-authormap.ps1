# Written Using ChatGPT 3.5, Based on GreenRaccoon23's Response on Stack Overflow https://stackoverflow.com/questions/4592866/git-how-to-estimate-a-contribution-of-a-person-to-my-project-in-terms-of-added
# With Author Map

# Define a function to parse the git log and gather statistics for each user
function Get-GitLogStats {
    param (
        [string[]]$Args
    )

    # Define a hashtable to map variations of author names to a standard name
    $authorMap = @{
        "Thomas Orth" = "Thomas Orth"
        "Tom Orth" = "Thomas Orth"
        "KaileyCozart" = "KaileyCozart"
        "AnishKV1230" = "AnishKV1230"
        "Anish" = "AnishKV1230"
        "Grossman, Elan" = "Grossman, Elan"
        "Jacob Shimer" = "Jacob Shimer"
        "nkapila6" = "nkapila6"
        "taelerq" = "taelerq"
        "benjamyu" = "benjamyu"
        "Charlie Clark" = "Charlie Clark"
        "Anita Cheung" = "Anita Cheung"
        "Kausar Patherya" = "Kausar Patherya"
        "deatheragetr" = "deatheragetr"
    }

    # Get the git log with author information and numstat
    $log = git log --pretty=format:'%an' --numstat @Args

    # Initialize user statistics hashtable
    $userStats = @{}
    $currentAuthor = ''

    # Process each line in the git log
    foreach ($line in $log -split '\r?\n') {
        if ($line -match '^[^\d]') {
            # This line is an author name
            $author = $line.Trim()
            if ($authorMap.ContainsKey($author)) {
                $currentAuthor = $authorMap[$author]
            } else {
                $currentAuthor = $author
            }

            if (-not $userStats.ContainsKey($currentAuthor)) {
                $userStats[$currentAuthor] = [PSCustomObject]@{
                    FilesChanged = 0
                    Insertions = 0
                    Deletions = 0
                }
            }
        } elseif ($line -match '^\d+\s+\d+\s+.+') {
            # This line is a numstat entry
            $fields = $line -split '\s+'
            $insertions = [int]$fields[0]
            $deletions = [int]$fields[1]

            # Update user statistics
            $userStats[$currentAuthor].FilesChanged++
            $userStats[$currentAuthor].Insertions += $insertions
            $userStats[$currentAuthor].Deletions += $deletions
        }
    }

    # Output the stats per user with the sum of insertions and deletions
    foreach ($user in $userStats.Keys) {
        $stats = $userStats[$user]
        $totalChanges = $stats.Insertions + $stats.Deletions
        Write-Output "${user}: $($stats.FilesChanged) files changed, $($stats.Insertions) insertions(+), $($stats.Deletions) deletions(+), $totalChanges total changes"
    }
}

# Call the function with all passed arguments
Get-GitLogStats $args