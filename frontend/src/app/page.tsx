"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { MapPin, Search, Users, Utensils, Star, Clock, Euro, Navigation } from "lucide-react"
import LocationSelector from "@/components/location-selector"
import CuisineSelector from "@/components/cuisine-selector"
import SettingSelector from "@/components/setting-selector"
import UserSelector from "@/components/user-selector"
import RestaurantResults from "@/components/restaurant-results"

interface Preferences {
  price: number[]
  distance: number[]
  rating: number[]
  waitTime: number[]
}

interface SearchCriteria {
  location: string
  cuisines: string[]
  setting: string
  preferences: Preferences
  selectedUser: string
}

export default function RestaurantFinder() {
  const [activeTab, setActiveTab] = useState("criteria")
  const [searchCriteria, setSearchCriteria] = useState<SearchCriteria>({
    location: "",
    cuisines: [],
    setting: "",
    preferences: {
      price: [50],
      distance: [50],
      rating: [50],
      waitTime: [50],
    },
    selectedUser: "",
  })

  const handleLocationChange = (location: string) => {
    setSearchCriteria((prev) => ({ ...prev, location }))
  }

  const handleCuisinesChange = (cuisines: string[]) => {
    setSearchCriteria((prev) => ({ ...prev, cuisines }))
  }

  const handleSettingChange = (setting: string) => {
    setSearchCriteria((prev) => ({ ...prev, setting }))
  }

  const handlePreferenceChange = (key: keyof Preferences, value: number[]) => {
    setSearchCriteria((prev) => ({
      ...prev,
      preferences: { ...prev.preferences, [key]: value },
    }))
  }

  const handleUserChange = (user: string) => {
    setSearchCriteria((prev) => ({ ...prev, selectedUser: user }))
  }

  const handleSearch = () => {
    setActiveTab("results")
  }

  const isSearchReady = searchCriteria.location || searchCriteria.selectedUser

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-red-50 p-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Restaurant Finder</h1>
          <p className="text-lg text-gray-600">Find the perfect restaurant for any occasion</p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="criteria" className="flex items-center gap-2">
              <Search className="w-4 h-4" />
              Search criteria
            </TabsTrigger>
            <TabsTrigger value="results" className="flex items-center gap-2">
              <Utensils className="w-4 h-4" />
              Results
            </TabsTrigger>
          </TabsList>

          <TabsContent value="criteria" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MapPin className="w-5 h-5 text-orange-500" />
                    Location (Required)
                  </CardTitle>
                  <CardDescription>Choose a restaurant, enter a place, or name a city</CardDescription>
                </CardHeader>
                <CardContent>
                  <LocationSelector onLocationChange={handleLocationChange} />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="w-5 h-5 text-blue-500" />
                    Restaurant Recommendation
                  </CardTitle>
                  <CardDescription>Or select a user for similar recommendations</CardDescription>
                </CardHeader>
                <CardContent>
                  <UserSelector onUserChange={handleUserChange} />
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Optional filters</CardTitle>
                <CardDescription>Refine your search with additional criteria</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <Label className="text-base font-medium mb-3 block">Cuisine</Label>
                  <CuisineSelector onCuisinesChange={handleCuisinesChange} />
                </div>

                <Separator />

                <div>
                  <Label className="text-base font-medium mb-3 block">Setting</Label>
                  <SettingSelector onSettingChange={handleSettingChange} />
                </div>

                <Separator />

                <div>
                  <Label className="text-base font-medium mb-4 block">Weight Preferences</Label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <Label className="flex items-center gap-2">
                          <Euro className="w-4 h-4" />
                          Price
                        </Label>
                        <span className="text-sm text-gray-500">{searchCriteria.preferences.price[0]}%</span>
                      </div>
                      <Slider
                        value={searchCriteria.preferences.price}
                        onValueChange={(value) => handlePreferenceChange("price", value)}
                        max={100}
                        step={10}
                        className="w-full"
                      />
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <Label className="flex items-center gap-2">
                          <Navigation className="w-4 h-4" />
                          Distance
                        </Label>
                        <span className="text-sm text-gray-500">{searchCriteria.preferences.distance[0]}%</span>
                      </div>
                      <Slider
                        value={searchCriteria.preferences.distance}
                        onValueChange={(value) => handlePreferenceChange("distance", value)}
                        max={100}
                        step={10}
                        className="w-full"
                      />
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <Label className="flex items-center gap-2">
                          <Star className="w-4 h-4" />
                          Rating
                        </Label>
                        <span className="text-sm text-gray-500">{searchCriteria.preferences.rating[0]}%</span>
                      </div>
                      <Slider
                        value={searchCriteria.preferences.rating}
                        onValueChange={(value) => handlePreferenceChange("rating", value)}
                        max={100}
                        step={10}
                        className="w-full"
                      />
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <Label className="flex items-center gap-2">
                          <Clock className="w-4 h-4" />
                          Cuisine Similarity
                        </Label>
                        <span className="text-sm text-gray-500">{searchCriteria.preferences.waitTime[0]}%</span>
                      </div>
                      <Slider
                        value={searchCriteria.preferences.waitTime}
                        onValueChange={(value) => handlePreferenceChange("waitTime", value)}
                        max={100}
                        step={10}
                        className="w-full"
                      />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {(searchCriteria.location ||
              searchCriteria.selectedUser ||
              searchCriteria.cuisines.length > 0 ||
              searchCriteria.setting) && (
              <Card>
                <CardHeader>
                  <CardTitle>Current Selection</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {searchCriteria.location && (
                      <Badge variant="secondary" className="flex items-center gap-1">
                        <MapPin className="w-3 h-3" />
                        {searchCriteria.location}
                      </Badge>
                    )}
                    {searchCriteria.selectedUser && (
                      <Badge variant="secondary" className="flex items-center gap-1">
                        <Users className="w-3 h-3" />
                        {searchCriteria.selectedUser}
                      </Badge>
                    )}
                    {searchCriteria.cuisines.map((cuisine) => (
                      <Badge key={cuisine} variant="outline">
                        {cuisine}
                      </Badge>
                    ))}
                    {searchCriteria.setting && <Badge variant="outline">{searchCriteria.setting}</Badge>}
                  </div>
                </CardContent>
              </Card>
            )}

            <div className="flex justify-center">
              <Button onClick={handleSearch} disabled={!isSearchReady} size="lg" className="px-8">
                <Search className="w-4 h-4 mr-2" />
                Find Restaurants
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="results">
            <RestaurantResults searchCriteria={searchCriteria} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}