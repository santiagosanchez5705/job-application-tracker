# AI Usage Documentation

## Tools Used

I used Claude Code in the terminal to help set up MySQL Server and MySQL Workbench, understand Flask and the application structure, develop UI ideas, generate frontend and database code, and debug problems. I also asked Claude to explain how the generated code worked and how the different technologies connected.

## Key Prompts

The following are paraphrased examples of the main questions and requests I gave Claude:

1. "How do I set up MySQL Server on Windows, and how is it different from MySQL Workbench?"
2. "How do I connect Workbench to my local MySQL Server and open my project's database?"
3. "Explain how Flask works and how a route connects an HTML form to Python code and a database query."
4. "Help me create the required companies, jobs, applications, and contacts tables and explain their relationships."
5. "Suggest UI ideas for a job application tracker and help turn my layout and styling ideas into HTML and CSS."
6. "Help generate the database queries for adding, viewing, editing, and deleting records, and explain how they work."
7. "Explain this error and help me debug the database connection, SQL query, or Flask route causing it."
8. "Walk me through how the code works, including the JSON fields and the job skill-matching calculation."

## What Worked Well

Claude's main code-generation assistance was creating frontend HTML/CSS,  Flask backend, and database schema and query code. It helped turn my UI ideas into working page layouts and forms, and explained how the database code connected to Flask. Its debugging explanations helped me understand errors and decide what needed to change.

## What I Modified

I directed revisions to the generated interface based on my own layout and styling ideas. I also used follow-up requests to adjust the generated code to the project's required tables, fields, and behavior. These revisions were developed with Claude's help rather than treating its initial output as the finished project.

## Lessons Learned

### Foreign keys and deletion policies

I developed a better understanding of how primary keys identify records and foreign keys enforce relationships. Foreign keys help prevent references to nonexistent records, but they do not enforce every business rule. I also learned why deletion policies require a deliberate choice: RESTRICT protects dependent records, while CASCADE can remove related rows automatically. A confirmation screen and database constraints serve different purposes.

### Parameterized queries and validation

Parameterization separates values from SQL syntax and handles inputs such as names containing apostrophes.

### Connecting the application to the database

I learned to separate the roles of MySQL Server, Workbench, and the Python connector. Server manages the database, Workbench is a client for inspecting and querying it, and the connector lets Flask communicate with it. They must use the intended server, port, database, and credentials. This also helped me distinguish authentication failures from a stopped server or an incorrect database name. Workbench does not need to stay open for Flask to access a running MySQL Server.

### Flask and the request flow

I learned how a browser request reaches a Flask route, how the route reads and validates form data, and how database results are passed to an HTML template. Jinja templates let pages display changing data while reusing a shared layout. I also learned why redirecting after a successful form submission helps prevent accidental resubmission on refresh, and why browser-side validation must be supported by checks in the backend.

### Skill matching and edge cases

I learned that a skill-match percentage depends on a clearly defined denominator: the number of required skills for a job. Trimming whitespace, comparing consistently across capitalization, and removing duplicates prevents formatting differences from changing results. Empty skill lists also need explicit handling so the calculation does not divide by zero or imply a match without supporting data. Explaining these cases helped me understand the algorithm beyond its basic percentage formula.

### Using AI to understand and improve code

I learned that AI assistance was more useful when I asked for explanations of specific functions, queries, and errors instead of only requesting finished code. Working through the connection between the interface, Flask, and MySQL helped me understand why a change in one layer could affect another. I also learned to treat generated code as something to review and test, especially for database changes where a successful-looking page does not by itself prove that the correct data was saved.