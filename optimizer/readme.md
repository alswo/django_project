차량경로안내
----------------------------------

+ 기본정보

| Name | Description |
| ---- | --- |
| Resource URI	         |  http://devel-tayotayo.edticket.com/getRoute?algorithm={algorithm} |
| Protocol/HTTP Method   |  REST / Post Method |
| Version             	 |  1 |
| Pre-Conditions	       | 1) Request Header accept 의 값으로 다음의 값을 지원 합니다. - application/json : json 포맷의 데이터 응답. (Default) |
    

+ Querystring Parameters

|      Name        | DataType                     | Mandatory          | Example    | Default | Description |
| ---------------- | ---------------------------- | ------------------ | ---------- | ------- | ----------- | 
| algorithm | `String`            | N | salesman | prim | 길찾기 알고리즘  |


+ Request Payload

|      Name        | DataType                     | Mandatory          | Example    | Default | Description |
| ---------------- | ---------------------------- | ------------------ | ---------- | ------- | ----------- | 
| startName | `String`            | Y | %EC%B6%9C%EB%B0%9C |  | 출발지 명칭 UTF-8 인코딩 해야 합니다. |
| startX | `String`            | Y |14148317.661607 |  | 출발지 X좌표: 경도 |
| startY | `String`            | Y | 4494878.084352 |  | 출발지 Y좌표: 위도 |
| endName | `String`            | Y | %EC%B6%9C%EB%B0%9C |  | 도착지 명칭 UTF-8 인코딩 해야 합니다. |
| endX | `String`            | Y |14148317.661607 |  | 도착지 X좌표: 경도 |
| endY | `String`            | Y | 4494878.084352 |  | 도착지 Y좌표: 위도 |
| viaPoints | `Node`            | Y |  |  | 경유지 목록 입니다. 목록 전체는 대괄호[] 각각의 리스트는 중괄호{}로 묶습니다. |
| viaPointName | `String`            | Y | test01 |  | 경유지 명칭 |
| viaPointX | `String`            | Y | 14148809.322692 |  | 경유지 X좌표 |
| viaPointY | `String`            | Y | 4493197.096773 |  | 경유지 Y좌표 |

+ Request Sample Code
```
{
  "startX": "14148317.661607", 
  "startY": "4494878.084352", 
  "endY": "4494726.671574", 
  "endX": "14148219.329390", 
  "startName": "Start", 
  "endName": "End", 
  "viaPoints": 
  [
    {
      "viaPointName": "test01", 
      "viaPointY": "4493197.096773", 
      "viaPointX": "14148809.322692"
    }, 
    {
      "viaPointName": "test02", 
      "viaPointY": "4493893.745713", 
      "viaPointX": "14147628.099206"
    }
  ]
}
```

+ Response Parameter

|      Name        | DataType                     | Mandatory          | Example    | Default | Description |
| ---------------- | ---------------------------- | ------------------ | ---------- | ------- | ----------- | 
| type | `String`            | Y | FeatureCollection |  | geojson 표준 프로퍼티입니다. |
| properties | `Node`            | N |  |  | 사용자 정의 프로퍼티 목록 입니다.  |
| \| totalTime | `String`            | Y |  |  | 경로 총 소요 시간(단위:초)입니다 |
| features | `Node`            | N |  |  | 포인트 및 라인의 형상 정보입니다. (geojson 표준 규격) |
| \| properties | `Node`            | N | |  | 사용자 정의 프로퍼티 정보입니다. (geojson 표준 규격) |
| \|\|index | `Number`            | N | 1 |  | 경로 순번입니다. |
| \|\|viaPointName | `String`            | N |  |  | 경유지 이름 입니다. |
| \|\|requiredTime | `Number`            | N |  |  | 경유지 소요시간 |
