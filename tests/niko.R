data = read.csv("/tmp/w/niko.csv", header=FALSE)
names(data) <- c("Sender", "Relative Time")
# convert to minutes
data$`Relative Time` <- data$`Relative Time`/60
ALLOWED_CHAT_DELAY = 10
hist(data$`Relative Time`[data$`Relative Time` > ALLOWED_CHAT_DELAY], breaks=1000, ylim=c(0,23), xlim=c(0,5000))
help(hist)
# convert to hours
data$`Relative Time` <- data$`Relative Time`/60
ALLOWED_CHAT_DELAY = 0.2
hist(data$`Relative Time`[data$`Relative Time` > ALLOWED_CHAT_DELAY], breaks=2000, ylim=c(0,23), xlim=c(0,40))

hist(data$`Relative Time`[data$`Relative Time` > 0.5 & data$`Relative Time` < 7], breaks=2000)
r <- data$`Relative Time`
length(r)
sum(r < 0.25)
hist(r, breaks=4000)
hist(r[r > 0.5], breaks=2000)
hist(r[r > 0.5], breaks=2000, xlim=c(0,100))
hist(r[r > 0.5 & r < 7], breaks=60)
sum(r > 0.5 & r < 7)
sum(r >= 7 & r < 24)
