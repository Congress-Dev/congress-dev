FROM node

RUN curl -o- -L https://yarnpkg.com/install.sh | bash

COPY package.json /usr/src/app/package.json
COPY yarn.lock /usr/src/app/yarn.lock
WORKDIR /usr/src/app
RUN yarn install

COPY .env /usr/src/app/.env
COPY ./src /usr/src/app/src
COPY ./public /usr/src/app/public
COPY ./start.sh /usr/src/app/start.sh

ENTRYPOINT ["bash", "start.sh"]