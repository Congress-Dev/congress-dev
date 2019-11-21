FROM node

RUN curl -o- -L https://yarnpkg.com/install.sh | bash
WORKDIR /usr/src/app

COPY yarn.lock /usr/src/app/yarn.lock
RUN yarn install

COPY . /usr/src/app


ENTRYPOINT [ "bash" ]