
The prupose of this tool is to transfer the RT tickets to a Kibana instance where we can look for older cases and solutions.
It was an exisiting script. My task was to refactor it and add more functionality.

This includes:

Create a migration script what provides possibility to transfer object from ELK-ELK or from index-index (No opetion from RT recovery, it stores the ticket contents for a limited amount of time)
Separating queues, system componenets to provide better option for seearching.
Add option to filter out specific objects.
Simplify the old code, test it and make sure it runs on our server without any issue. 
Clean out and rework the ELK instance what stores the tickets.