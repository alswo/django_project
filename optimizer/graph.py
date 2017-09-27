#!/usr/bin/python
#_*_ coding:utf-8 _*_

import sys
import requests
import simplejson
import json

class Vertex:
    def __init__(self, node):
        self.id = node
        self.adjacent = {}
        # Set distance to infinity for all nodes
        self.distance = sys.maxint
        # Mark all nodes unvisited        
        self.visited = False  
        # Predecessor
        self.previous = None

    def add_neighbor(self, neighbor, weight=0):
        self.adjacent[neighbor] = weight

    def get_connections(self):
        return self.adjacent.keys()  

    def get_id(self):
        return self.id

    def get_weight(self, neighbor):
        return self.adjacent[neighbor]

    def set_distance(self, dist):
        self.distance = dist

    def get_distance(self):
        return self.distance

    def set_previous(self, prev):
        self.previous = prev

    def set_visited(self):
        self.visited = True

    def __str__(self):
        return str(self.id) + ' adjacent: ' + str([x.id for x in self.adjacent])

class Graph:
    def __init__(self):
        self.vert_dict = {}
        self.num_vertices = 0

    def __iter__(self):
        return iter(self.vert_dict.values())

    def add_vertex(self, node):
        self.num_vertices = self.num_vertices + 1
        new_vertex = Vertex(node)
        self.vert_dict[node] = new_vertex
        return new_vertex

    def get_vertex(self, n):
        if n in self.vert_dict:
            return self.vert_dict[n]
        else:
            return None

    def add_edge(self, frm, to, cost = 0):
        if frm not in self.vert_dict:
            self.add_vertex(frm)
        if to not in self.vert_dict:
            self.add_vertex(to)

        self.vert_dict[frm].add_neighbor(self.vert_dict[to], cost)
        self.vert_dict[to].add_neighbor(self.vert_dict[frm], cost)

    def get_vertices(self):
        return self.vert_dict.keys()

    def set_previous(self, current):
        self.previous = current

    def get_previous(self, current):
        return self.previous

class ResultSet:
    def __init__(self, v, w):
        self.vertices = v
        self.weight = w

    def set_vertices(v):
        self.vertices = v

    def set_weight(w):
        self.weight = w

class PoiVertex(Vertex):
    def __init__(self, node, lon, lat, numpassenger):
        self.id = node
        self.adjacent = {}
        # Set distance to infinity for all nodes
        self.distance = sys.maxint
        # Mark all nodes unvisited        
        self.visited = False  
        # Predecessor
        self.previous = None
        self.numpassenger = int(numpassenger)

        self.lon = lon
        self.lat = lat


class PoiGraph(Graph):
    def __init__(self, reqCoordType="EPSG3857"):
        self.vert_dict = {}
        self.num_vertices = 0
        self.reqCoordType = reqCoordType
        
    def add_vertex(self, node, lon, lat, numpassenger):
        self.num_vertices = self.num_vertices + 1
        new_vertex = PoiVertex(node, lon, lat, numpassenger)
        self.vert_dict[node] = new_vertex
        return new_vertex

    def set_everyweight(self):

    	#urlstr = "http://route-tayotayo.edticket.com:8080/routes/routeSequential30?version=1"
    	#urlstr = "https://apis.skplanetx.com/tmap/routes"
	urlstr = "http://route-tayotayo.edticket.com:8080/routes"
	payload = {'appKey': '9c78e49d-c72c-36a6-8e25-5c249e9291a3', 'version': '1', 'reqCoordType': self.reqCoordType}
        #r = requests.get(urlstr, params=payload)
        #r.json()
        for v in self.get_vertices():
            vertex = self.get_vertex(v)
            for n in self.get_vertices():
                neighbor = self.get_vertex(n)
                if vertex.get_id() == neighbor.get_id():
                    continue
                if neighbor in vertex.get_connections():
                    continue

                payload['startX'] = vertex.lon
                payload['startY'] = vertex.lat
                payload['endX'] = neighbor.lon
                payload['endY'] = neighbor.lat

		try:
                	r = requests.get(urlstr, params=payload, timeout=1)
                	if r.status_code == requests.codes.ok:
                    		response = r.json()
                    		weight = response['features'][0]['properties']['totalTime']
                	else:
                    		weight = 0
		except:
			weight = 0

                self.add_edge(v, n, weight)
		#sys.stderr.write("[" + v + "]->[" + n + "]\n")

    def get_json(self, objparam, routes):
        total_weight = 0
        obj = objparam
        obj['features'] = list()
        obj['properties'] = {}
        obj['type'] = "FeatureCollection"
        if len(routes) > 1:
            prev_vertex = None
            index = 0
            for route in routes:
                weight = 0
                ## for startName
                if index == 0:
                    prev_vertex = self.get_vertex(route)
                else:
                    current_vertex = self.get_vertex(route)
                    weight = current_vertex.get_weight(prev_vertex)
                    total_weight += weight
                    prev_vertex = self.get_vertex(route)
                obj['features'].append({'index': index, 'viaPointName': route, 'requiredTime': weight, 'lat': self.get_vertex(route).lat, 'lng': self.get_vertex(route).lon})
                index += 1
            obj['properties']['totalTime'] = total_weight
        return json.dumps(obj)

    def get_totalpassenger(self):
        total_passenger = 0

        for v in self.get_vertices():
            vertex = self.get_vertex(v)
            total_passenger += vertex.numpassenger

        return total_passenger

def shortest(v, path):
    ''' make shortest path from v.previous'''
    if v.previous:
        path.append(v.previous.get_id())
        shortest(v.previous, path)
    return

import heapq

def dijkstra(aGraph, start):
    print '''Dijkstra's shortest path'''
    # Set the distance for the start node to zero 
    start.set_distance(0)

    # Put tuple pair into the priority queue
    unvisited_queue = [(v.get_distance(),v) for v in aGraph]
    heapq.heapify(unvisited_queue)

    while len(unvisited_queue):
        # Pops a vertex with the smallest distance 
        uv = heapq.heappop(unvisited_queue)
        current = uv[1]
        current.set_visited()

        #for next in v.adjacent:
        for next in current.adjacent:
            # if visited, skip
            if next.visited:
                continue
            new_dist = current.get_distance() + current.get_weight(next)
            
            if new_dist < next.get_distance():
                next.set_distance(new_dist)
                next.set_previous(current)
                print 'updated : current = %s next = %s new_dist = %s' \
                        %(current.get_id(), next.get_id(), next.get_distance())
            else:
                print 'not updated : current = %s next = %s new_dist = %s' \
                        %(current.get_id(), next.get_id(), next.get_distance())

        # Rebuild heap
        # 1. Pop every item
        while len(unvisited_queue):
            heapq.heappop(unvisited_queue)
        # 2. Put all vertices not visited into the queue
        unvisited_queue = [(v.get_distance(),v) for v in aGraph if not v.visited]
        heapq.heapify(unvisited_queue)

def findMin(aGraph):
    visited_list = [v for v in aGraph if v.visited]
    minWeight = 1000000
    minVertex = None
    for v in visited_list:
        for n in v.adjacent:
            if (n.visited):
                continue
	    w = v.get_weight(n)
	    if (minWeight >= w):
                minWeight = w
                minVertex = n

    if minVertex == None:
        return None

    minVertex.set_visited()
    #result = ResultSet(minVertex, minWeight)
    #return result
    return minVertex

def prim(aGraph, start, end):
    print '''Prim's MST'''
    result = list()
    ## Set the distance for the start node to zero 
    start.set_visited()
    result.append(start.get_id())
   
    ## not to visit
    end.set_visited()

    n = findMin(aGraph)
    while (n != None):
        result.append(n.get_id())
        n = findMin(aGraph)

    result.append(end.get_id())

    return result

# recursive function
# travel to adjacent vertex
def travel(aGraph, vertex, endvertex, weight, visited):
    visitedlist = list()
    visitedlist.extend(visited)
    visitedlist.append(vertex)

    resultlist = list()

    
    ## point name 을 vertex 의 key 로 저장하다보니 start 와 end 가 동일할 경우 처리가 어려움
    mm = 1
    if (visitedlist[0] == endvertex):
        mm = 0

    if ((len(aGraph.get_vertices())-mm)== len(visitedlist)) :
        resultset = ResultSet(visitedlist, weight)
        resultlist.append(resultset)
        return resultlist


    #sys.stderr.write ("vertex = " + vertex.get_id() + "\n")
    #sys.stderr.write ("len(get_vertices) = " + str(len(aGraph.get_vertices())) + "\n")
    #sys.stderr.write ("len(visitedlist) = " + str(len(visitedlist)) + "\n")
    #for v in aGraph.get_vertices():
        #sys.stderr.write ("v[" + v + "]\n")
    #for v in visitedlist:
        #sys.stderr.write ("list[" + v.get_id() + "]\n")

    for n in vertex.adjacent:
        if n in visitedlist:
            continue 
        if n == endvertex:
            continue

        #sys.stderr.write ("travel(), n = " + n.get_id() + ":" + str(len(visitedlist)) + "\n")
        result = travel(aGraph, n, endvertex, weight + vertex.get_weight(n), visitedlist)
        if (result != None):
            resultlist.extend(result)

    return resultlist

def cmp_resultset(a, b):
    if a.weight > b.weight:
        return 1
    elif a.weight == b.weight:
        return 0
    else:
        return -1

def travelling_salesman(aGraph, start, end):
    # n!
    print '''Travelling Salesman'''

    visited = list()
    result = list()

    resultlist = travel(aGraph, start, end, 0, visited)
    print (len(resultlist))

    for resultset in resultlist:
        end_vertex = resultset.vertices[len(resultset.vertices)-1]
        resultset.vertices.append(end)
        resultset.weight += end_vertex.get_weight(end)

    resultlist.sort(cmp_resultset)
    for v in resultlist[0].vertices:
        result.append(v.get_id())

    return result

# recursive function
# travel to adjacent vertex
def mintime_travel(aGraph, vertex, endvertex, weight, numpassenger, visited):
    visitedlist = list()
    visitedlist.extend(visited)
    visitedlist.append(vertex)

    resultlist = list()

    ## point name 을 vertex 의 key 로 저장하다보니 start 와 end 가 동일할 경우 처리가 어려움
    mm = 1
    if (visitedlist[0] == endvertex):
        mm = 0

    if ((len(aGraph.get_vertices())-mm)== len(visitedlist)) :
        resultset = ResultSet(visitedlist, weight)
        resultlist.append(resultset)
        return resultlist

    for n in vertex.adjacent:
        if n in visitedlist:
            continue 
        if n == endvertex:
            continue

        result = mintime_travel(aGraph, n, endvertex, weight + vertex.numpassenger * vertex.get_weight(n), numpassenger + vertex.numpassenger, visitedlist)
        if (result != None):
            resultlist.extend(result)

    return resultlist

def mintime_passenger(aGraph, start, end):
    # n!
    print '''Mintime Passenger'''

    visited = list()
    result = list()

    total_passenger = aGraph.get_totalpassenger()

    resultlist = mintime_travel(aGraph, start, end, 0, 0, visited)

    for resultset in resultlist:
        end_vertex = resultset.vertices[len(resultset.vertices)-1]
        resultset.vertices.append(end)
        resultset.weight += total_passenger * end_vertex.get_weight(end)
        print resultset.weight
        for v in  resultset.vertices:
		print v

    resultlist.sort(cmp_resultset)
    for v in resultlist[0].vertices:
        result.append(v.get_id())

    return result

## return the average absolute deviation of the list
def aad (lst):
    temp = []
    mean = sum(lst) / float(len(lst))
    for i in range(len(lst)):
        temp.append(float(abs(lst[i] - mean)))
    return sum(temp)/ len(lst)

## return the variance of the list
def variance(lst):
    temp = []
    mean = sum(lst) / float(len(lst))
    for i in range(len(lst)):
        temp.append(float(abs(lst[i] - mean)) ** 2)

## return the standard deviation of the list
def stddev(lst):
    return variance(lst)**0.5

def standard_deviation(aGraph, start, end):
    # n!
    print '''Standard Deviation'''

    visited = list()
    result = list()

    resultlist = travel(aGraph, start, end, 0, visited)

    # 모든 경우의 route list 를 만듬
    for resultset in resultlist:
        next_vertex = end
        until_weight = 0
        total_percent = 0
        percent_list = list()
        for vertex in reversed(resultset.vertices):
            if (vertex == end):
                deviation = 0
                percent = 0
            else:
                deviation = vertex.get_weight(next_vertex) + until_weight - vertex.get_weight(end)
                if (vertex.get_weight(end) == 0):
                    percent = 1
                else:
                    percent =  round((deviation *100.0 / vertex.get_weight(end)), 2)
            percent_list.append(percent)
            total_percent += percent
            until_weight += vertex.get_weight(next_vertex)
            next_vertex = vertex

        resultset.vertices.append(end)
        resultset.weight = variance(percent_list)

    resultlist.sort(cmp_resultset)
    for v in resultlist[0].vertices:
        result.append(v.get_id())

    return result


if __name__ == '__main__':

    #g = Graph()

    #g.add_vertex('a')
    #g.add_vertex('b')
    #g.add_vertex('c')
    #g.add_vertex('d')
    #g.add_vertex('e')
    #g.add_vertex('f')

    #g.add_edge('a', 'b', 7)  
    #g.add_edge('a', 'c', 9)
    #g.add_edge('a', 'f', 14)
    #g.add_edge('b', 'c', 10)
    #g.add_edge('b', 'd', 15)
    #g.add_edge('c', 'd', 11)
    #g.add_edge('c', 'f', 2)
    #g.add_edge('d', 'e', 6)
    #g.add_edge('e', 'f', 9)

    g = PoiGraph()

    #received_json_data = {"reqCoordType":"WGS84GEO","resCoordType":"WGS84GEO","startName":"롯데슈퍼 마두점S","startX":"126.78855157890416","startY":"37.65634555673625","endName":"롯데슈퍼 마두점E","endX":"126.78855157890416","endY":"37.65634555673625","viaPoints":[{"viaPointName":"신한은행ATM 숲속마을3단지지점1","viaPointId":"신한은행ATM 숲속마을3단지지점","index":0,"viaX":"126.79587345576675","viaY":"37.66746213182238"},{"viaPointName":"초가집부동산2","viaPointId":"초가집부동산","index":1,"viaX":"126.78136699892669","viaY":"37.67008120080965"},{"viaPointName":"냉천초교사거리3","viaPointId":"냉천초교사거리","index":2,"viaX":"126.78628980707647","viaY":"37.66726844410171"},{"viaPointName":"일산풍동성원상떼빌5차아파트4","viaPointId":"일산풍동성원상떼빌5차아파트","index":3,"viaX":"126.79618620241394","viaY":"37.665844531450055"},{"viaPointName":"숲속마을9단지성원상떼빌아파트5","viaPointId":"숲속마을9단지성원상떼빌아파트","index":4,"viaX":"126.80349292119143","viaY":"37.673205346565005"},{"viaPointName":"위시티4단지자이아파트6","viaPointId":"위시티4단지자이아파트","index":5,"viaX":"126.81491126609298","viaY":"37.67979023664351"},{"viaPointName":"요진와이하우스아파트7","viaPointId":"요진와이하우스아파트","index":6,"viaX":"126.78788057333918","viaY":"37.675369262123496"},{"viaPointName":"일산위시티자이1단지아파트8","viaPointId":"일산위시티자이1단지아파트","index":7,"viaX":"126.81193195989","viaY":"37.683425402573185"},{"viaPointName":"신한은행ATM 숲속마을3단지지점9","viaPointId":"신한은행ATM 숲속마을3단지지점","index":8,"viaX":"126.79587345576675","viaY":"37.66746213182238"},{"viaPointName":"초가집10","viaPointId":"초가집","index":9,"viaX":"126.78603613240159","viaY":"37.648372776944214"},{"viaPointName":"성원1차아파트11","viaPointId":"성원1차아파트","index":10,"viaX":"126.7956692115661","viaY":"37.664261523640405"},{"viaPointName":"하늘마을5단지휴먼시아아파트12","viaPointId":"하늘마을5단지휴먼시아아파트","index":11,"viaX":"126.78777150159623","viaY":"37.67703766117442"},{"viaPointName":"하늘마을1단지휴먼시아아파트13","viaPointId":"하늘마을1단지휴먼시아아파트","index":12,"viaX":"126.78003518085113","viaY":"37.680378598312835"}]}
    received_json_data = {"reqCoordType":"WGS84GEO","resCoordType":"WGS84GEO","startName":"롯데슈퍼 마두점S","startX":"126.78855157890416","startY":"37.65634555673625","endName":"롯데슈퍼 마두점E","endX":"126.78855157890416","endY":"37.65634555673625","viaPoints":[{"viaPointName":"신한은행ATM 숲속마을3단지지점1","viaPointId":"신한은행ATM 숲속마을3단지지점","index":0,"viaX":"126.79587345576675","viaY":"37.66746213182238"},{"viaPointName":"초가집부동산2","viaPointId":"초가집부동산","index":1,"viaX":"126.78136699892669","viaY":"37.67008120080965"},{"viaPointName":"냉천초교사거리3","viaPointId":"냉천초교사거리","index":2,"viaX":"126.78628980707647","viaY":"37.66726844410171"},{"viaPointName":"일산풍동성원상떼빌5차아파트4","viaPointId":"일산풍동성원상떼빌5차아파트","index":3,"viaX":"126.79618620241394","viaY":"37.665844531450055"},{"viaPointName":"숲속마을9단지성원상떼빌아파트5","viaPointId":"숲속마을9단지성원상떼빌아파트","index":4,"viaX":"126.80349292119143","viaY":"37.673205346565005"},{"viaPointName":"위시티4단지자이아파트6","viaPointId":"위시티4단지자이아파트","index":5,"viaX":"126.81491126609298","viaY":"37.67979023664351"},{"viaPointName":"요진와이하우스아파트7","viaPointId":"요진와이하우스아파트","index":6,"viaX":"126.78788057333918","viaY":"37.675369262123496"},{"viaPointName":"일산위시티자이1단지아파트8","viaPointId":"일산위시티자이1단지아파트","index":7,"viaX":"126.81193195989","viaY":"37.683425402573185"},{"viaPointName":"신한은행ATM 숲속마을3단지지점9","viaPointId":"신한은행ATM 숲속마을3단지지점","index":8,"viaX":"126.79587345576675","viaY":"37.66746213182238"},{"viaPointName":"초가집10","viaPointId":"초가집","index":9,"viaX":"126.78603613240159","viaY":"37.648372776944214"},{"viaPointName":"성원1차아파트11","viaPointId":"성원1차아파트","index":10,"viaX":"126.7956692115661","viaY":"37.664261523640405"},{"viaPointName":"하늘마을5단지휴먼시아아파트12","viaPointId":"하늘마을5단지휴먼시아아파트","index":11,"viaX":"126.78777150159623","viaY":"37.67703766117442"}]}

    g.add_vertex(received_json_data['startName'], received_json_data['startX'], received_json_data['startY'], 0)
    for viaPoint in received_json_data['viaPoints']:
        if 'viaPoints' not in viaPoint:
            numPassenger = '1'
        else:
            numPassenger = viaPoint['viaPointNumPassenger']
        g.add_vertex(viaPoint['viaPointName'], viaPoint['viaX'], viaPoint['viaY'], numPassenger)
    g.add_vertex(received_json_data['endName'], received_json_data['endX'], received_json_data['endY'], 0)

     

    #g.add_vertex('A', '14148317.661607', '4494878.084352', 0)
    #g.add_vertex('B', '14148809.322692', '4493197.096773', 1)
    #g.add_vertex('C', '14148219.329390', '4494726.671574', 10)
    #g.add_vertex('D', '14147628.099206', '4493893.745713', 0)

    g.set_everyweight()

    #print 'Graph data:'
    #for v in g:
        #for w in v.get_connections():
            #vid = v.get_id()
            #wid = w.get_id()
            #print '( %s , %s, %3d)'  % ( vid, wid, v.get_weight(w))

            
    #result = travelling_salesman(g, g.get_vertex('원마을현대힐스테이트'), g.get_vertex('판교도서관'))
    #result = travelling_salesman(g, g.get_vertex(received_json_data['startName']), g.get_vertex(received_json_data['endName']))
    result = prim(g, g.get_vertex(received_json_data['startName']), g.get_vertex(received_json_data['endName']))
    #result = standard_deviation(g, g.get_vertex('A'), g.get_vertex('A'))
    print result
    #travelling_salesman(g, g.get_vertex('원마을현대힐스테이트'))

    #print(simplejson.dumps(obj))

