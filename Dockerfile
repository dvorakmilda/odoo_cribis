FROM registry.gitlab.com/26house/odoo/repo_pull_mirroring/odooaa:14 as builder

USER root

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# Generate locale C.UTF-8 for postgres and general locale data
ENV LANG="C.UTF-8"

# Copy module and depenedency modules to tmp image
COPY ./ /mnt/extra-addons/odoo_cribis

# Separate module from depenedencies
RUN mkdir /tmp/odoo_cribis && cd /mnt/extra-addons/ && tar cf - --exclude .git --exclude=dep_modules odoo_cribis | tar xf - -C /tmp && chown --recursive odoo:odoo /tmp/odoo_cribis

# Copy module and dependencies into separate dirs
FROM registry.gitlab.com/26house/odoo/repo_pull_mirroring/odooaa:14
USER root
# Install debug lib
# RUN pip3 install debugpy
RUN apt update
RUN apt -y install git-all
RUN pip3 install ptvsd
RUN pip3 install xmltodict


COPY --from=builder /tmp/odoo_cribis /mnt/extra-addons/odoo_cribis
COPY --from=builder /mnt/extra-addons/odoo_cribis/dep_modules /26houseModules

# Set permissions for addons
RUN chown --recursive odoo:odoo /26houseModules/ /mnt/extra-addons/

# Mount /var/lib/odoo to allow restoring filestore, mount /mnt/extra-addons for enterprise addons
VOLUME ["/var/lib/odoo", "/mnt/extra-addons"]

# Expose Odoo services
EXPOSE 8069 8071 8072

# Set default user when running the container
USER odoo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]


