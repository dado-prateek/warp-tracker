CREATE DATABASE warp;

CREATE TABLE warp_torrents (
    id              int,
    filename        varchar(255),
    peers           int,
    seeds           int,
    dl_count        int,
    size            int,
    up_date         timestamp
);

