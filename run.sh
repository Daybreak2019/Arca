

Interval=$1
TotalSize=$2

for((Num=0;Num<=$TotalSize;Num+=Interval));  
do
End=$[Num+Interval]
python arca.py -s clone -b Num -e $End -d
done 


