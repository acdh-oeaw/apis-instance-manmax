Running local instance
======================

Development is carried out using a containerised application with VSCode and Docker.

Make sure you have VSCode [https://code.visualstudio.com/] and Docker Desktop [https://www.docker.com/products/docker-desktop/] installed.

In VSCode, install the `Dev Containers` plugin.


1. Clone the repo with the `dev` branch: `git clone --branch dev https://github.com/acdh-oeaw/apis-instance-manmax.git`
2. Open the cloned `apis-instance-manmax` directory with VSCode.
3. In the Command Pallette in VSCode, run `Dev Containers: Rebuild and Reopen in Container`
4. Wait while the container builds
5. Open the VSCode built-in Terminal (Terminal > New Terminal)
6. Once built, migrate the database with `django-admin migrate`
7. Build relationship-type objects with `django-admin create_relationships`
8. Run `python apis_ontology/model_config.py`
9. To run the application, run `django-admin runserver`


