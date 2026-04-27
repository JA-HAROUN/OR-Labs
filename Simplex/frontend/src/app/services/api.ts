import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { SimplexRequest, SimplexResponse } from '../models/simplex.model';

@Injectable({
  providedIn: 'root',
})
export class Api {
  private apiUrl = 'http://localhost:5000/api/solve';

  constructor(private http: HttpClient) {}

  solveSimplex(data: SimplexRequest): Observable<SimplexResponse> {
    return this.http.post<SimplexResponse>(this.apiUrl, data);
  }
}
