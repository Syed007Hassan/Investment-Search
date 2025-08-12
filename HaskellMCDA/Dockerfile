FROM haskell:9.6 as build

WORKDIR /app

# Copy cabal files first for better caching
COPY haskell-mcda.cabal /app/haskell-mcda.cabal
COPY Setup.hs /app/Setup.hs
RUN cabal update

# Copy source
COPY src /app/src

# Install binary into a known location
RUN cabal install exe:haskell-mcda --installdir=/root/.local/bin --overwrite-policy=always

# Use the same image as runtime for simplicity
FROM haskell:9.6
WORKDIR /app

COPY --from=build /root/.local/bin/haskell-mcda /usr/local/bin/haskell-mcda

EXPOSE 8081
CMD ["haskell-mcda"]

