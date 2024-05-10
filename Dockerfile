FROM debian:bullseye-slim
MAINTAINER Mwiti Mugao. <mwitiernest@gmail.com>

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# Generate locale C.UTF-8 for postgres and general locale data
ENV LANG C.UTF-8

# Install some deps, lessc and less-plugin-clean-css, and wkhtmltopdf
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        dirmngr \
        fonts-noto-cjk \
        gnupg \
        libssl-dev \
        node-less \
        npm \
        python3-num2words \
        python3-pdfminer \
        python3-pip \
        python3-phonenumbers \
        python3-pyldap \
        python3-qrcode \
        python3-renderpm \
        python3-setuptools \
        python3-slugify \
        python3-vobject \
        python3-watchdog \
        python3-xlrd \
        python3-xlwt \
	python3-wheel \
        xz-utils \
	build-essential \
        autoconf \
        libtool \
        pkg-config \
        python3-dev \
        libldap2-dev \
        libsasl2-dev \
        libpq-dev \
    && curl -o wkhtmltox.deb -sSL https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.buster_amd64.deb \
    && echo 'ea8277df4297afc507c61122f3c349af142f31e5 wkhtmltox.deb' | sha1sum -c - \
    && apt-get install -y --no-install-recommends ./wkhtmltox.deb \
    && rm -rf /var/lib/apt/lists/* wkhtmltox.deb

# install latest postgresql-client
RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ bullseye-pgdg main' > /etc/apt/sources.list.d/pgdg.list \
    && GNUPGHOME="$(mktemp -d)" \
    && export GNUPGHOME \
    && repokey='B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8' \
    && gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "${repokey}" \
    && gpg --batch --armor --export "${repokey}" > /etc/apt/trusted.gpg.d/pgdg.gpg.asc \
    && gpgconf --kill all \
    && rm -rf "$GNUPGHOME" \
    && apt-get update  \
    && apt-get install --no-install-recommends -y postgresql-client \
    && rm -f /etc/apt/sources.list.d/pgdg.list \
    && rm -rf /var/lib/apt/lists/*

# Install rtlcss (on Debian buster)
RUN npm install -g rtlcss

# Install Odoo
# ENV ODOO_VERSION 15.0
# ARG ODOO_RELEASE=20240429
# ARG ODOO_SHA=ded89a7635233e5bcd27869f777980bf5a637b24
# RUN curl -o odoo.deb -sSL http://nightly.odoo.com/${ODOO_VERSION}/nightly/deb/odoo_${ODOO_VERSION}.${ODOO_RELEASE}_all.deb \
#    && echo "${ODOO_SHA} odoo.deb" | sha1sum -c - \
#    && apt-get update \
#    && apt-get -y install --no-install-recommends ./odoo.deb \
#    && rm -rf /var/lib/apt/lists/* odoo.deb

COPY ./odoo-15.0.post20240509 /opt/odoo

RUN useradd -m odoo && echo odoo:odoo | chpasswd

RUN pip3 install wheel
RUN pip3 install -r /opt/odoo/requirements.txt

RUN cp /opt/odoo/setup/odoo /opt/odoo/odoo-bin && chmod +x /opt/odoo/odoo-bin

# Copy entrypoint script and Odoo configuration file
COPY ./entrypoint.sh /
COPY ./odoo.conf /etc/odoo/

# Set permissions and Mount /var/lib/odoo to allow restoring filestore and /mnt/extra-addons for users addons
RUN chown odoo /etc/odoo/odoo.conf 
RUN mkdir -p /mnt/extra-addons 
RUN mkdir -p /var/lib/odoo
RUN chown -R odoo:odoo /mnt/extra-addons
RUN chown -R odoo:odoo /var/lib/odoo
RUN chmod 755 /mnt/extra-addons
RUN chmod 755 /var/lib/odoo

VOLUME ["/var/lib/odoo", "/mnt/extra-addons"]

# Expose Odoo services
EXPOSE 8069 8071 8072

# Set the default config file
ENV ODOO_RC /etc/odoo/odoo.conf

COPY wait-for-psql.py /usr/local/bin/wait-for-psql.py

RUN pip3 install simplejson

# Set default user when running the container
USER odoo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]
