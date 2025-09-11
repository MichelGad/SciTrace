# Glossary

This glossary defines technical terms and concepts used throughout SciTrace documentation.

## A

**API (Application Programming Interface)**
A set of protocols and tools for building software applications. SciTrace provides a RESTful API for programmatic access to all features.

**Authentication**
The process of verifying the identity of a user. SciTrace uses session-based authentication with Flask-Login.

**Authorization**
The process of determining what actions a user is allowed to perform. SciTrace implements role-based access control.

## B

**Blueprint**
A Flask feature that allows you to organize routes and related functionality into modules. SciTrace uses blueprints for modular route organization.

**Bootstrap**
A popular CSS framework used in SciTrace for responsive web design and UI components.

## C

**Commit**
In Git and DataLad, a commit represents a snapshot of your project at a specific point in time. SciTrace provides web-based commit management.

**Collaborator**
A user who has access to a project. Collaborators can have different permission levels (viewer, contributor, admin).

## D

**DataLad**
A data management system that builds on Git and Git-annex to provide data versioning, distribution, and reproducibility. SciTrace integrates seamlessly with DataLad.

**Dataflow**
A visual representation of a research workflow in SciTrace. Dataflows show the structure and relationships of your data files and processing steps.

**Dataset**
In DataLad, a dataset is a collection of files and directories that are version-controlled together. SciTrace automatically creates DataLad datasets for each dataflow.

**Directory Structure**
The organization of files and folders in a project. SciTrace creates different directory structures based on research type (Environmental, Biomedical, Computational, General).

## E

**Environmental Research**
One of the research types supported by SciTrace, focused on environmental monitoring, climate data, and ecological studies.

## F

**File Restoration**
The process of recovering deleted files from previous commits. SciTrace provides web-based file restoration with enhanced error handling.

**Flask**
A lightweight Python web framework used as the foundation of SciTrace's backend.

**Font Awesome**
A popular icon library used in SciTrace for clean, professional iconography.

## G

**Git**
A distributed version control system used by DataLad for tracking changes in files. SciTrace provides web-based Git operations.

**Git Log**
A command that shows the commit history of a repository. SciTrace provides an interactive Git log visualization with tree view and file diffs.

**Git-annex**
A tool for managing large files with Git. DataLad uses Git-annex for efficient handling of large data files.

## H

**HTTP Status Codes**
Standard codes returned by web servers to indicate the result of a request. SciTrace uses proper HTTP status codes in its API responses.

## I

**Interactive Visualization**
A dynamic, clickable representation of data structures. SciTrace provides interactive dataflow visualizations using Vis.js.

## J

**jQuery**
A JavaScript library used in SciTrace for DOM manipulation and AJAX requests.

**Jinja2**
A templating engine used by Flask for rendering HTML templates. SciTrace uses Jinja2 for its web interface.

## M

**Metadata**
Data that describes other data. SciTrace manages comprehensive metadata for files, including size, modification date, and tracking status.

**Modular Architecture**
A software design approach that separates functionality into independent, interchangeable modules. SciTrace uses modular architecture for better maintainability.

## N

**Network Visualization**
A graphical representation of data relationships as nodes and edges. SciTrace uses Vis.js for network visualization of dataflows.

**Node**
In network visualization, a node represents a file, directory, or processing step. SciTrace uses color-coded nodes to indicate different file types and statuses.

## O

**ORM (Object-Relational Mapping)**
A programming technique for converting data between incompatible type systems. SciTrace uses SQLAlchemy ORM for database operations.

## P

**Project**
The main organizational unit in SciTrace. Projects contain dataflows, tasks, and collaborators.

**PostgreSQL**
A powerful, open-source relational database system. SciTrace supports PostgreSQL for production deployments.

## R

**Research Type**
A classification system in SciTrace that determines the directory structure and organization of research projects. Types include Environmental, Biomedical, Computational, and General.

**RESTful API**
An architectural style for designing web services. SciTrace provides a RESTful API with proper HTTP methods and status codes.

**Repository**
In Git, a repository is a storage location for a project's files and their complete history. SciTrace creates Git repositories for each DataLad dataset.

## S

**SciTrace**
The name of the research data lineage platform. SciTrace provides tools for managing research data workflows with DataLad integration.

**SQLAlchemy**
A Python SQL toolkit and Object-Relational Mapping (ORM) library used by SciTrace for database operations.

**SQLite**
A lightweight, file-based database system. SciTrace uses SQLite for development and small deployments.

**Session**
A way to maintain state between HTTP requests. SciTrace uses sessions for user authentication and state management.

## T

**Task**
A unit of work within a project. Tasks in SciTrace can have deadlines, priorities, and assignees.

**Template**
In web development, a template is a file that defines the structure and layout of a web page. SciTrace uses Jinja2 templates for its web interface.

## U

**User**
An individual who has access to SciTrace. Users can have different roles (admin, user) and can be collaborators on projects.

**User Interface (UI)**
The visual and interactive elements of a software application. SciTrace provides a modern, responsive web interface.

## V

**Version Control**
A system for tracking changes to files over time. SciTrace uses Git and DataLad for comprehensive version control of research data.

**Vis.js**
A JavaScript library for network visualization used by SciTrace to create interactive dataflow diagrams.

**Virtual Environment**
An isolated Python environment that allows you to install packages without affecting the system Python installation. SciTrace uses virtual environments for dependency management.

## W

**Web Interface**
A user interface that runs in a web browser. SciTrace provides a comprehensive web interface for all operations.

**Web Server**
Software that serves web content to clients. SciTrace can be deployed with various web servers like Nginx or Apache.

**Workflow**
A sequence of connected steps that represent a process. In SciTrace, workflows are visualized as interactive dataflows.

## X

**XSS (Cross-Site Scripting)**
A security vulnerability that allows attackers to inject malicious scripts into web pages. SciTrace implements XSS prevention through template escaping and content security policies.

## Y

**YAML**
A human-readable data serialization format. SciTrace uses YAML for configuration files and deployment specifications.

## Z

**Zero-Configuration**
A system that works without requiring manual configuration. SciTrace provides zero-configuration setup for basic usage while allowing advanced configuration for production deployments.

---

**Need more definitions?** If you encounter a term not defined here, please create an issue in the repository or contribute to this glossary.
