from .workdays import WorkdaysFromSeconds


def sum_timetracking_for_jql(jira, query):
    issues = jira.search_issues(query,
                                maxResults=1000,
                                fields="aggregatetimeestimate,aggregatetimespent,aggregatetimeoriginalestimate")
    total_planned = sum(issue.fields.aggregatetimeoriginalestimate
                        if issue.fields.aggregatetimeoriginalestimate else 0
                        for issue in issues)
    total_spent = sum(issue.fields.aggregatetimespent
                      if issue.fields.aggregatetimespent else 0
                      for issue in issues)
    total_remaining = sum(issue.fields.aggregatetimeestimate
                          if issue.fields.aggregatetimeestimate else 0
                          for issue in issues)
    return {
        "original estimate": WorkdaysFromSeconds(total_planned),
        "time spent": WorkdaysFromSeconds(total_spent),
        "time remaining": WorkdaysFromSeconds(total_remaining),
    }
